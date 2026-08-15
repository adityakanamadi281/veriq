import * as React from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export function TagInput({
  values,
  onChange,
  placeholder,
  label,
  className,
}: {
  values: string[];
  onChange: (next: string[]) => void;
  placeholder?: string;
  label?: string;
  className?: string;
}) {
  const [draft, setDraft] = React.useState("");

  function commit() {
    const cleaned = draft.trim().replace(/,$/, "").trim();
    if (cleaned && !values.includes(cleaned)) {
      onChange([...values, cleaned]);
    }
    setDraft("");
  }

  function remove(v: string) {
    onChange(values.filter((x) => x !== v));
  }

  return (
    <div className={cn("space-y-1.5", className)}>
      {label && <label className="text-sm font-medium text-foreground">{label}</label>}
      <div className="flex flex-wrap items-center gap-1.5 rounded-md border border-input bg-card px-2 py-2 shadow-sm focus-within:border-ring focus-within:ring-2 focus-within:ring-ring/20">
        {values.map((v) => (
          <span
            key={v}
            className="inline-flex items-center gap-1 rounded-md bg-secondary px-2 py-0.5 text-[13px] text-secondary-foreground"
          >
            {v}
            <button
              type="button"
              onClick={() => remove(v)}
              className="text-muted-foreground transition-colors hover:text-foreground"
              aria-label={`Remove ${v}`}
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === ",") {
              e.preventDefault();
              commit();
            } else if (e.key === "Backspace" && !draft && values.length) {
              remove(values[values.length - 1]);
            }
          }}
          onBlur={commit}
          placeholder={values.length ? "" : placeholder}
          className="min-w-[120px] flex-1 bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground/70"
        />
      </div>
    </div>
  );
}
