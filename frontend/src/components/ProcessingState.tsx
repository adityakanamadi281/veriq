import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Calm, professional processing state. Uses the brief's recommended labels:
 * "Evaluating response", "Preparing next question", "Preparing your assessment".
 */
export function ProcessingState({
  label,
  description,
  className,
}: {
  label: string;
  description?: string;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-16 text-center animate-fade-in", className)}>
      <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" aria-hidden />
      <p className="mt-4 text-[15px] font-medium text-foreground">{label}</p>
      {description && (
        <p className="mt-1.5 max-w-sm text-sm leading-relaxed text-muted-foreground">
          {description}
        </p>
      )}
    </div>
  );
}
