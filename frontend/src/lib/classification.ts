import type { BadgeProps } from "@/components/ui/badge";
import type { ReadinessClassification } from "@/types";

export function classificationVariant(
  c: ReadinessClassification | string
): BadgeProps["variant"] {
  switch (c) {
    case "Ready":
      return "success";
    case "Developing":
      return "default";
    case "Emerging":
      return "warning";
    case "Foundational":
      return "danger";
    default:
      return "secondary";
  }
}

/** A restrained text tone for a score, used in bars and rings. */
export function scoreTone(score: number): string {
  if (score >= 75) return "text-success";
  if (score >= 60) return "text-foreground";
  if (score >= 45) return "text-warning";
  return "text-danger";
}

export function scoreBarColor(score: number): string {
  if (score >= 75) return "bg-success";
  if (score >= 60) return "bg-foreground";
  if (score >= 45) return "bg-warning";
  return "bg-danger";
}
