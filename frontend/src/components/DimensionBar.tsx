import { Badge } from "@/components/ui/badge";
import { classificationVariant, scoreBarColor } from "@/lib/classification";
import { cn } from "@/lib/utils";
import type { DimensionResult } from "@/types";

export function DimensionBar({ result }: { result: DimensionResult }) {
  return (
    <div className="py-3.5">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <span className="text-sm font-medium text-foreground">{result.dimension}</span>
          <Badge variant={classificationVariant(result.classification)} className="hidden sm:inline-flex">
            {result.classification}
          </Badge>
        </div>
        <span className="font-display text-sm font-semibold tabular-nums text-foreground">
          {result.score}
        </span>
      </div>
      <div className="mt-2.5 h-1.5 w-full overflow-hidden rounded-full bg-muted">
        <div
          className={cn("h-full rounded-full transition-all duration-700 ease-out", scoreBarColor(result.score))}
          style={{ width: `${result.score}%` }}
        />
      </div>
      {result.summary && (
        <p className="mt-2 text-[13px] leading-relaxed text-muted-foreground">{result.summary}</p>
      )}
    </div>
  );
}
