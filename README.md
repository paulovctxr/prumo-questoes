# PRUMO

![Visão geral do Prumo: questões, simulados e importação de conteúdo](docs/portfolio-overview.svg)

Plataforma de prática de matemática com banco de questões, filtros, listas e simulados. Combina uma interface em JavaScript com rotinas Python para preparação de conteúdo e integração com Supabase.

**[Abrir aplicação](https://prumo-questoes.vercel.app)** · [Código](https://github.com/paulovctxr/prumo-questoes)

> Endereço publicado no repositório. A autenticação depende da configuração do Supabase. A imagem acima apresenta o escopo do projeto; não é uma captura da interface.

## Funcionalidades

- Filtros por assunto e outros metadados das questões.
- Resolução de questões, registro de tentativas e consulta a comentários disponíveis.
- Listas, favoritos e simulados.
- Paginação, ordenação e controles de tamanho de texto.
- Carregamento sob demanda dos detalhes das questões de álgebra.
- Rotinas de extração, importação e revisão de conteúdo com Python.

## Tecnologias e arquitetura

| Parte | Tecnologias |
| --- | --- |
| Interface | HTML, CSS e JavaScript sem framework |
| Contas e banco | Supabase Auth, PostgreSQL e SQL |
| Preparação de conteúdo | Python e scripts auxiliares |
| Verificações | Node.js e Playwright |
| Publicação | Arquivos de `dist/` com configuração Vercel |

Tentativas e preferências da interface utilizam armazenamento local do navegador. A integração Supabase atende autenticação e consulta do banco; não se deve presumir sincronização de todo o progresso entre dispositivos.

## Executar localmente

Pré-requisitos: Git, Python 3, Bash e um projeto Supabase de desenvolvimento. Não há um `package.json` na raiz para iniciar a aplicação.

```sh
git clone https://github.com/paulovctxr/prumo-questoes.git
cd prumo-questoes
```

1. Em um projeto Supabase novo, siga [supabase/README.md](supabase/README.md) e aplique [supabase/schema.sql](supabase/schema.sql). As políticas SQL exigem atenção em bancos já configurados; não repita o schema sem revisar.
2. Configure as URLs de autenticação do seu ambiente no Supabase.
3. Defina os valores públicos usados no build:

```sh
export PRUMO_SUPABASE_URL="https://seu-projeto.supabase.co"
export PRUMO_SUPABASE_ANON_KEY="sua-chave-publica-anon"
bash build.sh
python3 -m http.server 8000 --directory dist
```

Abra `http://localhost:8000`. O build grava esses valores em `dist/index.html`; use somente chave pública com RLS configurado. Não grave chaves secretas no código.

## Roteiro de demonstração

1. Acesse uma conta no ambiente configurado.
2. Filtre questões por assunto e abra uma questão.
3. Selecione uma alternativa e consulte a correção ou resolução disponível.
4. Explore listas e simulados; algumas resoluções ainda podem estar pendentes.

## Estrutura

- `dist/`: aplicação estática e dados distribuídos ao navegador.
- `dist/bank-sync.js`: integração e carregamento do banco.
- `supabase/`: esquema e instruções de importação.
- `tools/`: extração, conversão, auditoria e verificações.
- `build.sh`: configuração pública de autenticação no HTML.
- `vercel.json`: saída `dist` e comando de build.

## Verificação e publicação

O teste [tools/test-bank.cjs](tools/test-bank.cjs) usa Node.js, Playwright, servidor em `http://127.0.0.1:8000/` e Chromium no caminho `/usr/bin/chromium`. Instale essas dependências em um ambiente de teste e ajuste o caminho do navegador se necessário antes de executar:

```sh
node tools/test-bank.cjs
```

O teste inclui expectativas específicas do conteúdo do banco. Não é um comando autocontido nem uma garantia de que os testes estejam passando nesta revisão de documentação.

Na Vercel, configure as duas variáveis `PRUMO_SUPABASE_*`; o `vercel.json` executa `bash build.sh` e publica `dist/`.

## Conteúdo e limitações

Consulte [o guia de importação](supabase/README.md) e [o fluxo de tratamento de álgebra](tools/README-tae.md). Diferencie dados importados, transcrições e resoluções revisadas. A existência de material no repositório não concede licença para redistribuir conteúdo de terceiros.
