import { scoreTone } from "@/lib/classification";
import { cn } from "@/lib/utils";

export function ScoreRing({
  score,
  size = 168,
  className,
}: {
  score: number;
  size?: number;
  className?: string;
}) {
  const stroke = 8;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(100, Math.max(0, score));
  const dash = (pct / 100) * circumference;

  return (
    <div
      className={cn("relative inline-flex items-center justify-center", className)}
      style={{ width: size, height: size }}
      role="img"
      aria-label={`Readiness score ${score} out of 100`}
    >
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          className={cn(scoreTone(score))}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${dash} ${circumference - dash}`}
          style={{ transition: "stroke-dasharray 0.9s ease-out" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="font-display text-5xl font-semibold tracking-tightish tabular-nums">
          {score}
        </span>
        <span className="mt-0.5 text-xs font-medium uppercase tracking-[0.12em] text-muted-foreground">
          Readiness
        </span>
      </div>
    </div>
  );
}
