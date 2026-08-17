import { Link } from "react-router-dom";
import { ArrowRight, Check } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";

const capabilities = [
  "Engineering Fundamentals",
  "Problem Solving",
  "AI Fluency",
  "Agentic Engineering",
  "Practical Reasoning",
  "Communication",
];

export function Landing() {
  const { user } = useAuth();
  const primaryTo = user ? "/app" : "/signup";

  return (
    <div className="flex min-h-screen flex-col">
      <header className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-primary-foreground text-[13px] font-semibold">
            A
          </span>
          <span className="font-display text-[15px] font-semibold tracking-tightish">VERIQ</span>
        </div>
        <div className="flex items-center gap-2">
          {user ? (
            <Button asChild variant="ghost" size="sm">
              <Link to="/app">Go to app</Link>
            </Button>
          ) : (
            <>
              <Button asChild variant="ghost" size="sm">
                <Link to="/signin">Sign in</Link>
              </Button>
              <Button asChild size="sm">
                <Link to="/signup">Get started</Link>
              </Button>
            </>
          )}
        </div>
      </header>

      <main className="flex flex-1 flex-col justify-center">
        <div className="container max-w-3xl py-20 sm:py-28">
          <p className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">
            AI Readiness Assessment
          </p>
          <h1 className="mt-5 font-display text-4xl font-semibold leading-[1.08] tracking-tightish text-balance sm:text-[44px]">
            Find out how ready you are for an AI-first engineering role.
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-relaxed text-muted-foreground text-balance">
            Understand your strengths, identify capability gaps, and receive a
            personalized readiness assessment — grounded in evidence, not vibes.
          </p>

          <div className="mt-9 flex flex-col items-start gap-3 sm:flex-row sm:items-center">
            <Button asChild size="lg" className="group">
              <Link to={primaryTo}>
                Start Assessment
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </Link>
            </Button>
            <span className="text-sm text-muted-foreground">
              No preparation needed · ~10 minutes
            </span>
          </div>

          <div className="mt-16 grid gap-2.5 sm:grid-cols-2">
            {capabilities.map((c) => (
              <div
                key={c}
                className="flex items-center gap-2.5 rounded-lg border border-border bg-card/60 px-3.5 py-2.5"
              >
                <Check className="h-4 w-4 text-muted-foreground" aria-hidden />
                <span className="text-sm text-foreground/90">{c}</span>
              </div>
            ))}
          </div>
        </div>
      </main>

      <footer className="border-t border-border py-6">
        <div className="container text-xs text-muted-foreground">
          VERIQ — an evidence-led, adaptive assessment. The interface stays calm;
          the intelligence shows through the result.
        </div>
      </footer>
    </div>
  );
}
