import * as React from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}

export function Dialog({ open, onOpenChange, children }: DialogProps) {
  React.useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onOpenChange(false);
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open, onOpenChange]);

  if (!open) return null;
  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-foreground/30 backdrop-blur-[2px] animate-fade-in"
        onClick={() => onOpenChange(false)}
      />
      <div
        role="dialog"
        aria-modal="true"
        className={cn(
          "relative z-10 w-full max-w-lg rounded-xl border border-border bg-card p-6 shadow-[0_24px_64px_-12px_hsl(var(--foreground)/0.3)] animate-fade-in"
        )}
      >
        {children}
      </div>
    </div>,
    document.body
  );
}

export function DialogHeader({ className, children }: { className?: string; children: React.ReactNode }) {
  return <div className={cn("mb-4 flex flex-col space-y-1.5", className)}>{children}</div>;
}

export function DialogTitle({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <h2 className={cn("font-display text-lg font-semibold tracking-tightish", className)}>{children}</h2>
  );
}

export function DialogDescription({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return <p className={cn("text-sm text-muted-foreground leading-relaxed", className)}>{children}</p>;
}

export function DialogClose({ onClick }: { onClick?: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="absolute right-4 top-4 text-muted-foreground transition-colors hover:text-foreground"
      aria-label="Close"
    >
      <X className="h-4 w-4" />
    </button>
  );
}
