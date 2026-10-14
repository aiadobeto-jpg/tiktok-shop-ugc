# Estudo de caso validado — MINISO X15 Pro

## Objetivo

Criar uma sequência de vídeos UGC para TikTok Shop/Reels usando o rosto do apresentador, com aparência natural de vídeo gravado por celular e sem texto sobreposto. O produto era um fone MINISO X15 Pro com estojo oval/arredondado e componentes curvos, um formato que se mostrou difícil de manter estável em geração de vídeo por IA.

Este documento registra o caminho completo: o que foi tentado, o que falhou, o que foi decidido, por que a solução funcionou e como repetir o processo com outra IA.

## Contexto inicial

A base de referência veio de vídeos comerciais anteriores e de uma análise quadro a quadro. A primeira ideia era aplicar uma estrutura de anúncio mais completa, com gancho, preço, demonstração, prova social, CTA e textos na tela.

Durante a revisão, essa estrutura foi ajustada. O preço nos primeiros segundos deixou de ser obrigatório, porque não combinava com o objetivo deste vídeo. Também foi decidido que o vídeo deveria ficar limpo, sem texto, sem cards, sem setas, sem legendas queimadas e sem excesso de elementos visuais.

A prioridade passou a ser:

> **rosto natural + produto fiel + curiosidade real + montagem limpa**

## O problema encontrado

O Flow conseguia gerar o apresentador, mas em várias tentativas substituía o fone por outro produto ou alterava o formato do estojo. O modelo tendia a:

- transformar o estojo em uma caixa retangular;
- alisar ou remover a textura curva da tampa;
- mudar a silhueta dos componentes;
- alterar a posição dos detalhes e da marca;
- criar outra unidade ou modificar o produto durante a manipulação;
- deformar o fone em cenas de aproximação ou encaixe na orelha.

Depois de duas tentativas com o mesmo erro, a decisão foi não continuar gastando gerações apenas repetindo o prompt. O problema principal não era falta de adjetivos: era a dificuldade do modelo em manter um objeto pequeno, curvo e com detalhes orgânicos durante ações complexas.

## Primeira solução considerada

O plano B mais seguro foi separar pessoa e produto:

1. gerar os primeiros segundos com o apresentador olhando para a câmera, sem o produto aparecer;
2. inserir depois uma foto real do fone na edição;
3. usar um corte ou movimento de câmera leve para integrar a foto à sequência.

Essa solução continua válida quando o modelo não consegue preservar o produto. Ela garante fidelidade total porque usa a imagem real, não uma recriação.

## Solução que finalmente funcionou

Antes de abandonar a geração integrada, foi feita uma última tentativa com uma ação muito mais simples:

- clipe de aproximadamente 8 segundos;
- plano único, sem cortes, sem transições e sem zoom brusco;
- produto começando fora do quadro e entrando apenas depois da abertura;
- descrição visual precisa do estojo;
- instrução repetida para não mudar a forma;
- nenhuma demonstração complexa de abrir, retirar ou colocar o fone na orelha;
- fala curiosa e natural, sem tom de vendedor;
- sem texto, música, legenda ou marca d’água.

O prompt descreveu o produto como um estojo oval/arredondado, preto fosco, com borda transparente, textura curva em relevo na tampa, marca MINISO e botão circular. Também proibiu explicitamente a transformação em caixa retangular, a simplificação para uma superfície lisa e a criação de uma segunda unidade.

O resultado correto veio quando o modelo recebeu uma única ação simples: o apresentador olha para a câmera, pega/mostra o produto e o aproxima gradualmente.

## Primeiro vídeo gerado

O primeiro clipe ficou com 8 segundos, em 9:16, com o apresentador no quarto e luz natural. A sequência visual foi:

1. apresentador olhando para a câmera e demonstrando curiosidade;
2. produto entrando em quadro;
3. estojo sendo mostrado à câmera;
4. aproximação gradual para revelar formato, textura e marca.

A fala ficou:

> “Cara, eu tava olhando uma coisa aqui e fiquei curioso. Olha isso aqui... o formato dele. Vou deixar marcado aqui pra vocês verem.”

O ponto mais importante foi que o produto permaneceu reconhecível. O rosto, a roupa preta, o quarto e a luz natural também ficaram consistentes.

## Segundo vídeo e continuidade

Para criar uma continuação, foi gerado outro clipe de 8 segundos. A ação foi reduzida ainda mais: o apresentador já começa segurando o estojo, olha para ele, olha para a câmera e faz apenas um pequeno ajuste da mão.

O diálogo planejado foi:

> “Fui olhar melhor e esse formato me chamou atenção. Tu já tinha visto um fone assim?”

O segundo prompt recebeu uma imagem de continuidade extraída do primeiro vídeo. A imagem foi escolhida em um momento que mostrava simultaneamente o rosto, a mão, o estojo, o cenário, a camisa e a iluminação.

A instrução de continuidade foi explícita:

> “Use the final frame of the previous video as the exact visual starting-point reference for this continuation. Match the presenter’s face position, camera framing, lighting, bedroom background, black shirt, hand position and product orientation as closely as possible.”

Aprendizado: escrever “continue o vídeo anterior” não é suficiente. Uma imagem concreta do estado final dá ao modelo uma âncora visual muito mais útil.

## Montagem final validada

Em vez de publicar dois clipes isolados de 8 segundos, foi feita uma montagem alternada:

> **parte do vídeo 1 → parte do vídeo 2 → retorno ao vídeo 1 → retorno ao vídeo 2**

A fala final ficou organizada assim:

1. “Cara, eu tava olhando uma coisa aqui e fiquei curioso.”
2. “Olha isso aqui.”
3. “Fui olhar melhor e esse formato me chamou atenção.”
4. “Tu já tinha visto um fone assim?”
5. “Vou deixar marcado aqui pra vocês verem.”

Essa montagem criou uma pequena conversa contínua e mais ritmo, sem exigir que um único clipe carregasse toda a história. Os cortes devem acontecer em pausas ou entre frases, nunca no meio de uma palavra.

## Decisões visuais definitivas

Para este caso, foram adotadas as seguintes decisões:

- formato vertical 9:16;
- clipes curtos de aproximadamente 8 segundos;
- aparência UGC de celular;
- luz natural de quarto;
- apresentador usando a mesma camiseta preta;
- fala em português brasileiro, com entrega espontânea;
- produto baseado nas imagens reais de referência;
- produto já na mão quando a ação for difícil;
- no máximo um movimento principal por clipe;
- sem texto na tela;
- sem legendas geradas pelo modelo;
- sem cards, setas, preços ou gráficos;
- sem música neste teste;
- apenas voz e ambiente natural;
- sem transições chamativas;
- cortes secos na montagem.

Essas decisões são uma base para este estilo, mas não precisam ser impostas a todo produto.

## O que não deve ser repetido

Não começar com o apresentador já manipulando o produto de forma complexa. Não pedir no mesmo clipe para pegar, abrir, retirar, colocar na orelha e mostrar detalhes. Não fazer close extremo quando o produto encaixa no corpo. Não confiar apenas em uma descrição textual quando há imagens reais disponíveis. Não insistir indefinidamente em novas gerações depois de o mesmo erro aparecer duas vezes.

Também não usar texto para compensar uma demonstração que não funciona. A solução correta é simplificar a ação, trocar o enquadramento ou resolver o trecho na edição.

## Processo recomendado para a próxima IA

### Antes da geração

1. Identificar qual detalhe do produto precisa ser preservado.
2. Separar fotos reais e nítidas do produto.
3. Decidir se o produto é fácil ou difícil de reproduzir.
4. Escrever uma fala curta, natural e falável.
5. Limitar cada clipe a uma ação principal.
6. Preparar a imagem de continuidade se for uma sequência.
7. Declarar que as imagens do produto são a fonte de verdade.
8. Proibir duplicação, troca, deformação e redesign do produto.

### Durante a geração

Usar prompts em inglês para as instruções de produção e manter o diálogo em português brasileiro entre aspas. Preferir um plano contínuo e uma câmera simples. Se a cena incluir um produto difícil, começar com ele já na mão e a uma distância confortável da câmera.

### Depois da geração

Conferir primeiro a fala e o lip sync. Em seguida, verificar o rosto, a roupa, o cenário e, principalmente, a silhueta do produto. Comparar o início e o fim do clipe para garantir que o produto não mudou. Se falhar duas vezes do mesmo modo, interromper a geração e migrar para uma ação mais simples ou para a foto real na montagem.

### Na edição

Montar os trechos com cortes secos. Cortar em pausas naturais. Nivelar o áudio entre clipes. Manter o ambiente sonoro coerente. Não adicionar elementos visuais que contrariem a proposta limpa. Se necessário, usar uma foto real do produto com movimento de câmera muito leve.

## Critério de sucesso

O vídeo não precisa parecer um comercial de televisão. Ele precisa parecer uma descoberta pessoal convincente. Para este caso, o sucesso foi definido por quatro condições:

1. o rosto e a atuação parecem naturais;
2. o MINISO X15 Pro permanece visualmente fiel;
3. a fala cria curiosidade e convida a uma resposta;
4. a montagem parece uma conversa contínua, sem poluição visual.

## Regra geral extraída do caso

> **Quando a IA erra um produto pequeno e orgânico, o melhor ajuste normalmente não é escrever um prompt maior. É reduzir a ação, dar prioridade às imagens reais, usar uma referência de continuidade e resolver o restante na edição.**

## Relação com o padrão geral

Este caso complementa o padrão geral de UGC do repositório. As regras de movimento, identidade e controle de qualidade continuam importantes, mas a estrutura de 20–25 segundos, preço nos primeiros segundos, prova social e CTA com card não deve ser imposta aqui. O usuário decidiu priorizar um vídeo limpo, de descoberta, sem texto na tela e sem venda agressiva.

A sequência do MINISO X15 Pro deve ser tratada como um exemplo de **UGC de descoberta em múltiplos clipes**, não como substituição universal do formato de anúncio completo.
