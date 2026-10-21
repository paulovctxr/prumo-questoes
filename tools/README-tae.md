# Coleção Tópicos de Álgebra Elementar

O PDF enviado pelo usuário é a fonte dos enunciados. Não transcrever fórmulas
automaticamente como se a extração textual fosse fiel: os exercícios usam
recortes rasterizados diretamente do PDF, com alternativas, diagramas e
notação originais. A identificação da obra é preservada; esses exercícios
não são chamados de inéditos.

## Regerar

Com Python 3, PyMuPDF e Pillow instalados:

```sh
python3 tools/export_tae.py /caminho/para/livro.pdf --output dist/livro-algebra
python3 tools/integrate_tae.py /caminho/para/livro.pdf
```

O arquivo de origem é a edição de 400 páginas enviada nesta conversa.
O hash SHA-256 está em `dist/livro-algebra/catalog.json`. O PDF original é
incluído no diretório da coleção para consulta da página completa.

`inventory_tae.py` reconhece os 20 capítulos e a sequência de 712 exercícios
propostos. Os exemplos resolvidos da parte teórica não são contados como
exercícios adicionais. Corrige o caso especial dos exercícios 1–10 do
capítulo de diofantinas, impressos antes do título da seção.

## Resoluções

As explicações elaboradas ficam em `tae-solutions*.json`, com chave
`primeira_pagina_do_capitulo:numero_da_questao`. Cada registro contém
`answer`, `steps` e, se necessário, `editorial_note`. Fórmulas usam `$...$`
e comandos LaTeX com barras escapadas conforme o formato JSON.

Estado atual: 127 resoluções elaboradas, de 712 exercícios. Capítulos
completos: conjuntos (34), módulo (30), equações do primeiro grau (32)
e diofantinas (31). Faltam 585 resoluções. A elaboração integral solicitada
pelo usuário continua pendente; não afirmar que todas estão prontas.

Os demais exercícios têm acesso às páginas de gabarito originais, com um
aviso explícito de ausência de resolução passo a passo. Não apresentar
esses gabaritos como soluções completas. O contador da interface é
calculado a partir dos registros efetivamente existentes.

Erros e ambiguidades identificados no livro são explicados sem alterar o
enunciado: exemplos incluem conjuntos 10, 17 e 34; módulo 5, 7, 8 e 10;
primeiro grau 10, 14, 26 e 27; diofantinas 13, 27 e 28.

## Aplicação e armazenamento

`bank-sync.js` registra os 712 exercícios no mesmo array `QUESTIONS`
do restante do acervo, com IDs estáveis e classificação nos assuntos já
existentes. Carrega somente os metadados necessários aos filtros, preferindo
`resumo_aplicacao` da tabela `questoes` do Supabase para usuários autenticados.
O enunciado, as imagens e os passos da resolução são buscados individualmente
em `dados_aplicacao` ao abrir a questão. Não há área, banner, rota ou
navegação separada para o livro.
`algebra-renderer.js` preserva os recortes originais dentro dos cartões de
questão normais e abre as resoluções no painel lateral existente.

Os filtros por assunto, instituição, tipo de questão e resolução usam os
mesmos registros. Exercícios discursivos permitem escrever uma resposta,
salva localmente, sem inventar correção automática. Somente questões com
alternativa correta identificada entram nos simulados de correção automática.
As fórmulas das explicações usam o KaTeX já instalado no site.

O arquivo `supabase/import_tae.sql` prepara a tabela existente `questoes`
para metadados e detalhes, permite gabarito nulo nas discursivas e insere os
712 registros. Preserva os demais IDs e interrompe toda a transação se um
ID pertencer a outra fonte. As políticas permitem leitura a autenticados;
não é criada permissão pública de escrita.

Não houve execução desse SQL no Supabase: esta sessão não dispõe de acesso
administrativo ao projeto. É necessário executá-lo uma vez no SQL Editor.
Até a importação, ou se o serviço estiver indisponível, o cliente usa
`questoes-algebra-index.json` e os arquivos individuais em `questoes-algebra/`.
Mesmo nessa alternativa, o lote completo não é incluído no JavaScript inicial.
O índice tem 386 KB sem compressão e cerca de 19 KB comprimido com gzip;
não contém enunciados, imagens nem resoluções. As imagens permanecem como
arquivos WebP e o Supabase guarda seus endereços, sem blobs no JSON.

Validação matemática: 889 expressões das 127 resoluções foram aceitas pelo
KaTeX; equações selecionadas foram conferidas com SymPy e contagens
diofantinas por enumeração independente. Os 712 registros são somados às
2.110 questões anteriores, totalizando 2.822 exercícios no banco da aplicação.

Execute `node tools/test-bank.cjs` com o servidor local na porta 8000 para
validar filtros, carregamento individual, respostas, simulados, layout móvel
e recuperação de falha. A consulta ao Supabase é testada com um cliente
simulado, inclusive sem os arquivos estáticos disponíveis, e não equivale
a uma importação ou validação no banco real. O SQL também foi validado
sintaticamente com o parser de PostgreSQL, incluindo os blocos PL/pgSQL.
