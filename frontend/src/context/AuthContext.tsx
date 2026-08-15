import * as React from "react";
import { getSupabase } from "@/lib/supabase";
import { config } from "@/lib/env";
import { setAuthTokenGetter } from "@/lib/api";

export interface AuthUser {
  id: string;
  email: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  loading: boolean;
  signUp: (email: string, password: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = React.createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<AuthUser | null>(null);
  const [token, setToken] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(true);

  // Register the token provider with the API layer once.
  React.useEffect(() => {
    setAuthTokenGetter(() => token);
  }, [token]);

  // Restore session on mount and subscribe to auth changes.
  React.useEffect(() => {
    let active = true;
    const supabase = getSupabase();
    if (!supabase) {
      setLoading(false);
      return;
    }

    (async () => {
      const { data } = await supabase.auth.getSession();
      const session = data.session;
      if (active && session) {
        setUser({ id: session.user.id, email: session.user.email || "" });
        setToken(session.access_token);
      }
      if (active) setLoading(false);
    })();

    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        setUser({ id: session.user.id, email: session.user.email || "" });
        setToken(session.access_token);
      } else {
        setUser(null);
        setToken(null);
      }
    });

    return () => {
      active = false;
      sub.subscription.unsubscribe();
    };
  }, []);

  const signUp = React.useCallback(async (email: string, password: string) => {
    const supabase = getSupabase();
    if (!supabase) throw new Error("Authentication is not configured.");
    const { data, error } = await supabase.auth.signUp({ email, password });
    if (error) throw error;
    if (data.session) {
      setUser({ id: data.session.user.id, email: data.session.user.email || "" });
      setToken(data.session.access_token);
    }
  }, []);

  const signIn = React.useCallback(async (email: string, password: string) => {
    const supabase = getSupabase();
    if (!supabase) throw new Error("Authentication is not configured.");
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    setUser({ id: data.session!.user.id, email: data.session!.user.email || "" });
    setToken(data.session!.access_token);
  }, []);

  const signOut = React.useCallback(async () => {
    await getSupabase()?.auth.signOut();
    setUser(null);
    setToken(null);
  }, []);

  const value: AuthContextValue = { user, token, loading, signUp, signIn, signOut };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}

export function isAuthConfigured() {
  return config.supabaseConfigured;
}
