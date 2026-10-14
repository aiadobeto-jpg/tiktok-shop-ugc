#!/usr/bin/env python3
"""frame_diff.py - QC medido de movimento para video UGC (TikTok Shop BR).

Responde tres perguntas com numero, nao com opiniao:

  1. O video congela em algum trecho? Por quanto tempo?
  2. Quanto do video e imagem parada?
  3. Os cortes acontecem no ritmo combinado (a cada 1-2s, nenhum plano acima de 2,5s)?

Reprovacao automatica (padrao deste projeto):

  - congelamento continuo >= 1,5s              -> REPROVA
  - qualquer congelamento nos ultimos 4s       -> REPROVA
  - imagem parada total >= 20% da duracao      -> REPROVA
  - algum plano acima de 2,5s                  -> AVISA (corte fora do ritmo)

Uso:

    python3 frame_diff.py final.mp4
    python3 frame_diff.py final.mp4 --csv qc.csv
    python3 frame_diff.py final.mp4 --json

Saida: resumo legivel no terminal, `qc.csv` ao lado do video (ou em --csv) e
codigo de saida 0 = aprovado, 1 = reprovado. O codigo de saida e o que torna
este script utilizavel dentro de um fluxo: `frame_diff.py final.mp4 || echo FALHOU`.

Como o numero e medido
----------------------

O video e decodificado em quadros de 160px de largura, em escala de cinza, na
taxa de amostragem pedida (padrao 10 qps). Para cada par de quadros
consecutivos calcula-se a diferenca absoluta media (0 = identico, 1 = preto
contra branco). Esse valor e o "movimento" entre os dois quadros.

  - "parado"  = movimento abaixo de --static-thr  (padrao 0.0035)
  - "congelado" = movimento abaixo de --freeze-thr (padrao 0.0015)
  - "corte"   = movimento acima de --cut-thr       (padrao 0.20)

Os limites sao absolutos e calibrados para video vertical de celular com
movimento constante. Eles nao sao sagrados: rode com `--report` num video que
voce ja sabe que esta bom e veja onde o numero cai. Se o seu material tiver
muito grao, suba os limites; se for muito limpo, desca.

Um limite absoluto unico erra em video escuro (pouco contraste) e em video com
muita textura. Por isso o resumo tambem imprime os percentis do movimento -
o p10 e o que diz se o "parado" do video e realmente parado ou se o limite
esta mal calibrado.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np


# ---------------------------------------------------------------- parametros

DEFAULT_FPS = 10.0
DEFAULT_FREEZE_THR = 0.0015
DEFAULT_STATIC_THR = 0.0035
DEFAULT_CUT_THR = 0.20
DEFAULT_FREEZE_SEC = 1.5
DEFAULT_TAIL_SEC = 4.0
DEFAULT_MAX_STATIC_PCT = 20.0
DEFAULT_MAX_SHOT_SEC = 2.5
DEFAULT_MIN_SHOT_SEC = 1.0
DEFAULT_WIDTH = 160


# ------------------------------------------------------------------ leitura

def _require(binary: str) -> None:
    if shutil.which(binary) is None:
        sys.exit(f"erro: `{binary}` nao encontrado no PATH. Instale o ffmpeg.")


def probe(path: Path) -> dict:
    """Duracao, resolucao, fps e numero de quadros, direto do container."""
    out = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration",
            "-of", "json", str(path),
        ],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        sys.exit(f"erro: ffprobe falhou em {path}\n{out.stderr.strip()}")

    streams = json.loads(out.stdout or "{}").get("streams") or [{}]
    s = streams[0]

    def _fps(value: str | None) -> float:
        if not value or "/" not in value:
            return 0.0
        num, _, den = value.partition("/")
        try:
            den_f = float(den)
            return float(num) / den_f if den_f else 0.0
        except ValueError:
            return 0.0

    return {
        "width": int(s.get("width") or 0),
        "height": int(s.get("height") or 0),
        "fps": _fps(s.get("r_frame_rate")),
        "nb_frames": int(s["nb_frames"]) if str(s.get("nb_frames", "")).isdigit() else None,
        "duration": float(s.get("duration") or 0.0),
    }


def scaled_height(orig_w: int, orig_h: int, width: int) -> int:
    """Altura alvo da reducao, mantendo a proporcao e forcando numero par.

    Calculada aqui, e nao deixada para o `scale=-2` do ffmpeg, porque um buffer
    de bytes nao diz qual e a altura: adivinhar a partir do tamanho do buffer
    encontra divisores errados e monta quadros fantasma.
    """
    if orig_w <= 0 or orig_h <= 0:
        sys.exit("erro: o video nao informou resolucao")
    height = int(round(orig_h * width / orig_w))
    if height % 2:
        height += 1
    return max(2, height)


def decode_gray(path: Path, fps: float, width: int, height: int) -> np.ndarray:
    """Decodifica o video em (n_quadros, altura, largura) uint8, escala de cinza."""
    cmd = [
        "ffmpeg", "-v", "error", "-i", str(path),
        "-vf", f"fps={fps},scale={width}:{height},format=gray",
        "-f", "rawvideo", "-",
    ]
    out = subprocess.run(cmd, capture_output=True)
    if out.returncode != 0:
        sys.exit(f"erro: ffmpeg falhou ao decodificar {path}\n"
                 f"{out.stderr.decode('utf-8', 'replace').strip()}")

    raw = np.frombuffer(out.stdout, dtype=np.uint8)
    frame_size = width * height
    if raw.size == 0 or raw.size % frame_size:
        sys.exit(
            f"erro: buffer decodificado com {raw.size} bytes nao fecha em quadros "
            f"de {width}x{height} ({frame_size} bytes)"
        )
    return raw.reshape(-1, height, width)


# ------------------------------------------------------------------- medidas

def motion_series(frames: np.ndarray) -> np.ndarray:
    """Movimento entre quadros consecutivos: media da diferenca absoluta / 255."""
    a = frames[:-1].astype(np.int16)
    b = frames[1:].astype(np.int16)
    return np.abs(a - b).mean(axis=(1, 2)) / 255.0


def runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """Trechos contiguos onde mask e True, como pares (inicio, fim exclusivo)."""
    if mask.size == 0:
        return []
    edges = np.flatnonzero(np.diff(np.concatenate(([False], mask, [False])).astype(np.int8)))
    return list(zip(edges[0::2].tolist(), edges[1::2].tolist()))


def shot_lengths(motion: np.ndarray, cut_thr: float, fps: float) -> list[float]:
    """Duracao de cada plano, em segundos, pelos cortes detectados."""
    cuts = np.flatnonzero(motion > cut_thr) + 1
    bounds = [0, *cuts.tolist(), len(motion) + 1]
    return [(b - a) / fps for a, b in zip(bounds[:-1], bounds[1:])]


# ------------------------------------------------------------------ relatorio

def analyse(path: Path, args: argparse.Namespace) -> tuple[dict, list[dict]]:
    info = probe(path)
    height = scaled_height(info["width"], info["height"], args.width)
    frames = decode_gray(path, args.fps, args.width, height)
    motion = motion_series(frames)

    n = motion.size
    sampled_sec = n / args.fps
    duration = info["duration"] or sampled_sec

    freeze_runs = runs(motion < args.freeze_thr)
    static_runs = runs(motion < args.static_thr)

    def longest(rs: list[tuple[int, int]]) -> float:
        return max((b - a for a, b in rs), default=0) / args.fps

    longest_freeze = longest(freeze_runs)
    longest_static = longest(static_runs)

    # ultimos N segundos: nada pode estar congelado
    tail_start = max(0, n - int(round(args.tail * args.fps)))
    tail_motion = motion[tail_start:]
    tail_frozen = tail_motion.size > 0 and bool((tail_motion < args.freeze_thr).any())
    tail_freeze_runs = runs(tail_motion < args.freeze_thr)
    tail_longest = longest(tail_freeze_runs)

    static_pct = 100.0 * float((motion < args.static_thr).mean()) if n else 0.0
    freeze_pct = 100.0 * float((motion < args.freeze_thr).mean()) if n else 0.0

    shots = shot_lengths(motion, args.cut_thr, args.fps)
    over_max = [s for s in shots if s > args.max_shot_sec]
    cuts_per_sec = (len(shots) - 1) / duration if duration else 0.0
    mean_shot = float(np.mean(shots)) if shots else 0.0

    fails: list[str] = []
    warns: list[str] = []

    if longest_freeze >= args.freeze_sec:
        fails.append(
            f"congelamento continuo de {longest_freeze:.2f}s "
            f"(limite {args.freeze_sec:.2f}s)"
        )
    if tail_frozen:
        fails.append(
            f"congelamento nos ultimos {args.tail:.0f}s: {tail_longest:.2f}s sem movimento"
        )
    if static_pct >= args.max_static_pct:
        fails.append(
            f"imagem parada em {static_pct:.1f}% do video "
            f"(limite {args.max_static_pct:.0f}%)"
        )
    if over_max:
        worst = max(over_max)
        warns.append(
            f"{len(over_max)} plano(s) acima de {args.max_shot_sec:.1f}s "
            f"(o maior tem {worst:.2f}s) - corte fora do ritmo"
        )
    elif len(shots) <= 1 and duration > args.max_shot_sec:
        warns.append(
            f"plano unico de {duration:.2f}s - nenhum corte detectado. "
            f"Se o video tiver cortes secos, baixe --cut-thr (atual {args.cut_thr})"
        )

    result = {
        "arquivo": path.name,
        "duracao_s": round(duration, 3),
        "resolucao": f'{info["width"]}x{info["height"]}',
        "fps_nativo": round(info["fps"], 3),
        "amostragem_qps": args.fps,
        "quadros_amostrados": int(n),
        "movimento_p10": round(float(np.percentile(motion, 10)), 5) if n else 0.0,
        "movimento_mediana": round(float(np.median(motion)), 5) if n else 0.0,
        "movimento_p90": round(float(np.percentile(motion, 90)), 5) if n else 0.0,
        "congelamento_mais_longo_s": round(longest_freeze, 2),
        "congelamento_total_pct": round(freeze_pct, 2),
        "parado_mais_longo_s": round(longest_static, 2),
        "parado_total_pct": round(static_pct, 2),
        "congelado_nos_ultimos_s": round(tail_longest, 2) if tail_frozen else 0.0,
        "planos": len(shots),
        "plano_medio_s": round(mean_shot, 2),
        "plano_mais_longo_s": round(max(shots), 2) if shots else 0.0,
        "cortes_por_segundo": round(cuts_per_sec, 2),
        "falhas": fails,
        "avisos": warns,
        "veredito": "REPROVADO" if fails else "APROVADO",
    }

    rows: list[dict] = []
    for i, m in enumerate(motion):
        t = i / args.fps
        state = "congelado" if m < args.freeze_thr else ("parado" if m < args.static_thr else "movimento")
        rows.append({
            "segundo": round(t, 3),
            "movimento": round(float(m), 5),
            "estado": state,
        })
    return result, rows


def report(result: dict, width: int = 74) -> None:
    line = "-" * width
    print(line)
    print(f"QC de movimento - {result['arquivo']}")
    print(line)
    print(f"  duracao            {result['duracao_s']:.2f}s  "
          f"({result['resolucao']} @ {result['fps_nativo']:.0f}fps)")
    print(f"  amostragem         {result['quadros_amostrados']} quadros @ "
          f"{result['amostragem_qps']:.0f}qps")
    print(f"  movimento          p10 {result['movimento_p10']:.5f} | "
          f"mediana {result['movimento_mediana']:.5f} | "
          f"p90 {result['movimento_p90']:.5f}")
    print(line)
    print(f"  congelamento       {result['congelamento_mais_longo_s']:.2f}s no pior trecho  |  "
          f"{result['congelamento_total_pct']:.1f}% do video")
    print(f"  imagem parada      {result['parado_mais_longo_s']:.2f}s no pior trecho  |  "
          f"{result['parado_total_pct']:.1f}% do video")
    print(f"  ultimos 4s         "
          f"{'congelado por ' + format(result['congelado_nos_ultimos_s'], '.2f') + 's' if result['congelado_nos_ultimos_s'] else 'sem congelamento'}")
    print(f"  planos             {result['planos']}  |  media {result['plano_medio_s']:.2f}s  |  "
          f"maior {result['plano_mais_longo_s']:.2f}s  |  "
          f"{result['cortes_por_segundo']:.2f} cortes/s")
    print(line)
    if result["falhas"]:
        print("  REPROVADO")
        for f in result["falhas"]:
            print(f"    - {f}")
    else:
        print("  APROVADO")
    for w in result["avisos"]:
        print(f"    aviso: {w}")
    print(line)


def main() -> int:
    p = argparse.ArgumentParser(
        description="QC medido de movimento para video UGC: acha congelamento e video parado.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("video", type=Path, help="caminho do video a medir")
    p.add_argument("--fps", type=float, default=DEFAULT_FPS,
                   help="quadros por segundo amostrados (suba para pegar congelamento curto)")
    p.add_argument("--width", type=int, default=DEFAULT_WIDTH,
                   help="largura da reducao usada para comparar os quadros")
    p.add_argument("--freeze-thr", type=float, default=DEFAULT_FREEZE_THR,
                   help="movimento abaixo disso conta como congelado")
    p.add_argument("--static-thr", type=float, default=DEFAULT_STATIC_THR,
                   help="movimento abaixo disso conta como parado")
    p.add_argument("--cut-thr", type=float, default=DEFAULT_CUT_THR,
                   help="movimento acima disso conta como corte")
    p.add_argument("--freeze-sec", type=float, default=DEFAULT_FREEZE_SEC,
                   help="congelamento continuo a partir disso reprova")
    p.add_argument("--tail", type=float, default=DEFAULT_TAIL_SEC,
                   help="janela final, em segundos, que nao pode congelar")
    p.add_argument("--max-static-pct", type=float, default=DEFAULT_MAX_STATIC_PCT,
                   help="percentual de imagem parada que reprova")
    p.add_argument("--max-shot-sec", type=float, default=DEFAULT_MAX_SHOT_SEC,
                   help="duracao de plano acima disso gera aviso")
    p.add_argument("--csv", type=Path, default=None,
                   help="onde gravar o CSV (padrao: qc.csv ao lado do video)")
    p.add_argument("--json", action="store_true", help="imprimir o resumo em JSON")
    p.add_argument("--report", action="store_true",
                   help="imprimir a curva de movimento quadro a quadro")
    args = p.parse_args()

    if not args.video.is_file():
        sys.exit(f"erro: {args.video} nao existe")
    _require("ffmpeg")
    _require("ffprobe")

    result, rows = analyse(args.video, args)

    csv_path = args.csv or args.video.with_name("qc.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["segundo", "movimento", "estado"])
        w.writeheader()
        w.writerows(rows)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        report(result)
        print(f"  csv: {csv_path}")

    if args.report:
        print()
        print("segundo  movimento  estado")
        for r in rows:
            bar = "#" * min(60, int(r["movimento"] * 400))
            print(f"{r['segundo']:7.2f}  {r['movimento']:.5f}  {r['estado']:<9} {bar}")

    return 1 if result["falhas"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
