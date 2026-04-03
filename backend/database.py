from supabase import create_client, Client
from config import settings

# Admin client (service role) - bypasses RLS, use carefully
supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)

# Anon client - respects RLS
supabase_anon: Client = create_client(settings.supabase_url, settings.supabase_anon_key)
