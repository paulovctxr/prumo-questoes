# Banco de questões do PRUMO

1. Crie um projeto no Supabase.
2. Abra o SQL Editor e execute `schema.sql`.
3. No painel da Vercel, crie `PRUMO_SUPABASE_URL` e `PRUMO_SUPABASE_ANON_KEY`.
4. Para o site estático, substitua os marcadores correspondentes em `dist/index.html` pelos valores públicos do projeto e faça um novo deploy.

A chave `anon` pode ficar no navegador quando as políticas RLS estiverem ativas. Nunca coloque a chave `service_role` no site.
