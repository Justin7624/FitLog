-- Run in your own Supabase SQL Editor. No service-role key is needed in the app.
create table if not exists public.fitlog_snapshots (
  user_id uuid primary key references auth.users(id) on delete cascade,
  revision integer not null default 1 check (revision > 0),
  payload jsonb not null,
  updated_at timestamptz not null default now()
);
alter table public.fitlog_snapshots enable row level security;
revoke all on public.fitlog_snapshots from anon;
grant select, insert, update on public.fitlog_snapshots to authenticated;
drop policy if exists fitlog_select_own on public.fitlog_snapshots;
create policy fitlog_select_own on public.fitlog_snapshots for select to authenticated using ((select auth.uid()) = user_id);
drop policy if exists fitlog_insert_own on public.fitlog_snapshots;
create policy fitlog_insert_own on public.fitlog_snapshots for insert to authenticated with check ((select auth.uid()) = user_id);
drop policy if exists fitlog_update_own on public.fitlog_snapshots;
create policy fitlog_update_own on public.fitlog_snapshots for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
