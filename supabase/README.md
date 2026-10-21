# Banco de questões do PRUMO

1. Crie um projeto no Supabase.
2. Abra o SQL Editor e execute `schema.sql`.
3. Na Vercel, crie `PRUMO_SUPABASE_URL` e `PRUMO_SUPABASE_ANON_KEY`.
4. Faça um novo deploy.

A chave `anon` pode ficar no navegador quando as políticas RLS estiverem
ativas. Nunca coloque a chave `service_role` no site.

## Importar ou corrigir os exercícios de álgebra

Execute `import_tae.sql` no SQL Editor do mesmo projeto. O script pode ser
executado novamente: ele atualiza os 712 IDs já importados e preserva os
demais registros.

As 712 questões são gravadas com dificuldade `difícil` e ano de aplicação
2026. O ano de publicação do livro permanece 2021 dentro dos metadados da
fonte.

Esta versão grava enunciados e alternativas como texto. Ela remove os antigos
endereços de fotografias integrais e de páginas do gabarito. Apenas questões
que dependem de um gráfico, diagrama ou tabela recebem o endereço de uma
captura pequena dessa parte visual.

Há 127 resoluções comentadas e 585 pendentes. O gabarito fotografado do livro
não é publicado. Questões sem resolução autoral não entram na correção
automática dos simulados.

O cliente consulta `resumo_aplicacao` para os filtros e `dados_aplicacao`
para carregar uma questão por vez. O SQL contém somente dados e deve ser
executado por quem tem acesso administrativo ao projeto.
