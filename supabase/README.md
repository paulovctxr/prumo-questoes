# Banco de questões do PRUMO

1. Crie um projeto no Supabase.
2. Abra o SQL Editor e execute `schema.sql`.
3. No painel da Vercel, crie `PRUMO_SUPABASE_URL` e `PRUMO_SUPABASE_ANON_KEY`.
4. Faça um novo deploy. O `build.sh` usa essas variáveis para configurar o cliente no HTML.

A chave `anon` pode ficar no navegador quando as políticas RLS estiverem ativas. Nunca coloque a chave `service_role` no site.

## Importar os exercícios de álgebra

Execute `import_tae.sql` no SQL Editor do mesmo projeto Supabase. O script
insere ou atualiza os 712 exercícios originais na tabela `questoes`, com
os assuntos usados pelo banco do site. Não remove os registros existentes.
Interrompe a transação se um dos IDs estiver ocupado por uma fonte diferente.

O cliente autenticado consulta `resumo_aplicacao` para os filtros e
`dados_aplicacao` para carregar um enunciado e sua resolução por vez.
As imagens já extraídas permanecem nos arquivos WebP do site; o banco
armazena seus endereços. Não é necessário gerar imagens por IA.

São 127 resoluções elaboradas e 585 ainda pendentes; a importação não cria
explicações que não foram escritas. Questões discursivas não recebem
gabarito numérico inventado e não entram na correção automática de simulados.

O SQL contém somente dados e não requer uma chave no navegador. Deve ser
executado por quem tem acesso administrativo ao projeto. Sua execução no
Supabase real não foi realizada nesta sessão. Enquanto a importação não
existe, o site usa um índice de metadados e carrega arquivos individuais
sob demanda, preservando o mesmo banco e os mesmos filtros.
