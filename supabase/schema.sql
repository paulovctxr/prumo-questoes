create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  name text,
  created_at timestamptz not null default now()
);

create table if not exists public.questoes (
  id bigint primary key,
  enunciado text not null,
  alternativas jsonb not null default '[]'::jsonb,
  gabarito integer check (gabarito >= 0),
  assunto text,
  subassunto text,
  instituicao text,
  ano integer,
  dificuldade text check (dificuldade in ('fácil','média','difícil')),
  figura_url text,
  resolucao text,
  fonte text,
  dados_aplicacao jsonb,
  resumo_aplicacao jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.profiles enable row level security;
alter table public.questoes enable row level security;

create policy "users read own profile" on public.profiles for select using (auth.uid() = id);
create policy "users update own profile" on public.profiles for update using (auth.uid() = id);
create policy "authenticated users read questions" on public.questoes for select to authenticated using (true);

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, name) values (new.id, new.raw_user_meta_data->>'name');
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
for each row execute procedure public.handle_new_user();
