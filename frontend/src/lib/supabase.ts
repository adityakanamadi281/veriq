import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { config } from "./env";

// Browser client uses the anon/publishable key only. Service-role credentials
// are never present in the frontend.
let client: SupabaseClient | null = null;

export function getSupabase(): SupabaseClient | null {
  if (!config.supabaseConfigured) return null;
  if (!client) {
    client = createClient(config.supabaseUrl!, config.supabaseAnonKey!, {
      auth: { persistSession: true, autoRefreshToken: true },
    });
  }
  return client;
}
