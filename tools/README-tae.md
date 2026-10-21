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

O item `Livro de Álgebra` da navegação carrega `catalog.json`, com filtros
de capítulo, busca, paginação e opção de mostrar apenas exercícios com
resolução. As fórmulas das explicações usam o KaTeX já instalado no site.

Esta integração usa os arquivos estáticos do site. Não houve inserção no
Supabase. O ambiente não tem credenciais administrativas do projeto,
e a tabela `questoes` atual não modela todos os tipos de exercícios
discursivos nem múltiplas respostas corretas.

Validação: 889 expressões das 127 resoluções foram aceitas pelo KaTeX;
equações selecionadas foram conferidas com SymPy e contagens diofantinas
por enumeração independente. O navegador confirmou os 712 registros,
filtros, paginação, gabaritos originais, visualização das soluções e layout
móvel, preservando o acervo anterior de 2.110 questões.
