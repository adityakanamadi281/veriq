// Runtime environment. Vite exposes only the browser-safe Supabase anon key.
// Gemini/service-role credentials never appear here — they are server-side only.

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

export const config = {
  apiUrl: (import.meta.env.VITE_API_URL as string | undefined) || "/api/v1",
  supabaseUrl,
  supabaseAnonKey,
  supabaseConfigured: Boolean(supabaseUrl && supabaseAnonKey),
};

export type AppConfig = typeof config;
