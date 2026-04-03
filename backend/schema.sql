-- Run this entire script in your Supabase SQL Editor
-- Go to: Supabase Dashboard → SQL Editor → New Query → Paste → Run

-- Enable pgvector extension
create extension if not exists vector;

-- Users table (extends Supabase auth)
create table if not exists public.profiles (
  id uuid references auth.users(id) on delete cascade primary key,
  email text not null,
  full_name text,
  role text default 'user' check (role in ('admin', 'user')),
  created_at timestamptz default now()
);

-- Documents table
create table if not exists public.documents (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) on delete cascade,
  title text not null,
  content text not null,
  source text default 'upload',
  file_type text,
  content_hash text unique,  -- for deduplication
  metadata jsonb default '{}',
  created_at timestamptz default now()
);

-- Embeddings table with pgvector
create table if not exists public.embeddings (
  id uuid default gen_random_uuid() primary key,
  document_id uuid references public.documents(id) on delete cascade,
  chunk_index int not null,
  chunk_text text not null,
  embedding vector(384),  -- SentenceTransformer all-MiniLM-L6-v2 dimension
  created_at timestamptz default now()
);

-- Search logs for analytics
create table if not exists public.search_logs (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) on delete set null,
  query text not null,
  results_count int,
  created_at timestamptz default now()
);

-- Q&A logs
create table if not exists public.qa_logs (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) on delete set null,
  question text not null,
  answer text,
  sources jsonb,
  created_at timestamptz default now()
);

-- Audit logs
create table if not exists public.audit_logs (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) on delete set null,
  action text not null,
  resource text,
  details jsonb,
  created_at timestamptz default now()
);

-- Create HNSW index for fast vector search
create index if not exists embeddings_vector_idx
  on public.embeddings using hnsw (embedding vector_cosine_ops);

-- Function: semantic search
create or replace function match_embeddings(
  query_embedding vector(384),
  match_threshold float default 0.3,
  match_count int default 5
)
returns table (
  document_id uuid,
  chunk_text text,
  similarity float,
  title text,
  source text,
  file_type text
)
language sql stable
as $$
  select
    e.document_id,
    e.chunk_text,
    1 - (e.embedding <=> query_embedding) as similarity,
    d.title,
    d.source,
    d.file_type
  from embeddings e
  join documents d on d.id = e.document_id
  where 1 - (e.embedding <=> query_embedding) > match_threshold
  order by e.embedding <=> query_embedding
  limit match_count;
$$;

-- Auto-create profile on signup
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.profiles (id, email, full_name, role)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'full_name', ''),
    'user'
  );
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- RLS Policies
alter table public.profiles enable row level security;
alter table public.documents enable row level security;
alter table public.embeddings enable row level security;
alter table public.search_logs enable row level security;
alter table public.qa_logs enable row level security;
alter table public.audit_logs enable row level security;

-- Profiles: users can read all, update own
create policy "profiles_select" on public.profiles for select using (true);
create policy "profiles_update" on public.profiles for update using (auth.uid() = id);

-- Documents: users see own, admins see all
create policy "documents_select" on public.documents for select
  using (auth.uid() = user_id or exists (
    select 1 from profiles where id = auth.uid() and role = 'admin'
  ));
create policy "documents_insert" on public.documents for insert
  with check (auth.uid() = user_id);
create policy "documents_delete" on public.documents for delete
  using (auth.uid() = user_id or exists (
    select 1 from profiles where id = auth.uid() and role = 'admin'
  ));

-- Embeddings: follow document access
create policy "embeddings_select" on public.embeddings for select using (true);
create policy "embeddings_insert" on public.embeddings for insert with check (true);
create policy "embeddings_delete" on public.embeddings for delete using (true);

-- Logs: users see own logs
create policy "search_logs_all" on public.search_logs for all using (auth.uid() = user_id);
create policy "qa_logs_all" on public.qa_logs for all using (auth.uid() = user_id);
create policy "audit_logs_select" on public.audit_logs for select using (auth.uid() = user_id);
create policy "audit_logs_insert" on public.audit_logs for insert with check (true);
