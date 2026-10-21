# Coleção Tópicos de Álgebra Elementar

As 712 questões ficam em `tae-transcriptions.json` como enunciados e
alternativas textuais. O site não publica fotografias dos enunciados, páginas
de gabarito ou uma cópia do PDF. Somente 17 questões com informação visual
indispensável usam uma captura recortada do gráfico, diagrama ou tabela.

Para regerar o índice, os detalhes sob demanda e o SQL do Supabase:

```sh
python3 tools/integrate_tae.py
```

`inventory_tae.py`, `transcribe_tae.py` e `extract_tae_figures.py` documentam
a migração inicial do PDF enviado pelo usuário. A regeneração normal usa
`tae-transcriptions.json` e `tae-figures.json`; não depende do PDF.

## Resoluções

As explicações elaboradas ficam em `tae-solutions*.json`. Cada registro tem
resposta, passos e, quando necessário, uma nota editorial. Fórmulas usam
LaTeX entre `$...$`.

Há 127 resoluções elaboradas. Faltam 585. Questões pendentes não exibem a
imagem do gabarito e não recebem resposta automática extraída do livro.
Somente uma resposta sustentada pela resolução elaborada pode ativar a
correção automática.

## Aplicação e armazenamento

`bank-sync.js` adiciona os 712 registros ao mesmo banco de questões e carrega
somente os metadados necessários aos filtros. O enunciado textual, a eventual
captura visual e a resolução são carregados individualmente ao abrir uma
questão. Não existe área, banner ou rota separada para o livro.

No banco da aplicação, as 712 questões são classificadas como `Difícil` e têm
2026 como ano de aplicação. O ano de publicação da fonte continua registrado
separadamente como 2021 nos metadados bibliográficos.

`supabase/import_tae.sql` insere ou atualiza os mesmos 712 IDs. Reexecutar o
arquivo substitui os antigos registros baseados em fotografias e limpa os
endereços de imagem integral. Os demais registros da tabela são preservados.

O fallback local usa `questoes-algebra-index.json` e os arquivos individuais
em `questoes-algebra/`. As 17 capturas recortadas somam cerca de 500 KB e são
baixadas somente nas questões que realmente precisam delas.

Estado matemático: 889 expressões das 127 resoluções foram aceitas pelo KaTeX;
equações selecionadas foram conferidas com SymPy e contagens diofantinas por
enumeração independente. O banco completo da aplicação tem 2.822 questões.

Execute `node tools/test-bank.cjs` com `dist` servido na porta 8000 para
validar filtros, carregamento individual, transcrições, figuras recortadas,
resoluções, simulados, layout móvel e o adaptador do Supabase.
