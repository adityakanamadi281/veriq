import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Check, AlertTriangle, Compass } from "lucide-react";
import { client } from "@/lib/client";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ScoreRing } from "@/components/ScoreRing";
import { DimensionBar } from "@/components/DimensionBar";
import { ProcessingState } from "@/components/ProcessingState";
import { ErrorState } from "@/components/Feedback";
import { classificationVariant } from "@/lib/classification";
import type { Pathway } from "@/types";

const PATHWAY_TONE: Record<Pathway, string> = {
  Ready: "text-success",
  "Targeted Capability Development": "text-foreground",
  "Structured Capability Development": "text-warning",
  "Foundation Development": "text-danger",
};

export function ResultPage() {
  const { id } = useParams();
  const { data: result, isLoading, isError, refetch } = useQuery({
    queryKey: ["result", id],
    queryFn: () => client.getResult(id!),
    enabled: !!id,
  });

  if (isLoading) return <PageContainer><ProcessingState label="Preparing your assessment" description="Reviewing your responses across the assessed capability areas." /></PageContainer>;
  if (isError) return <PageContainer><ErrorState message="We couldn’t load your result." onRetry={() => refetch()} /></PageContainer>;
  if (!result) return null;

  return (
    <PageContainer className="max-w-3xl">
      {/* Where do I stand? */}
      <section className="flex flex-col items-center text-center animate-fade-in">
        <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground">
          Your readiness
        </p>
        <ScoreRing score={result.overall_score} className="mt-5" />
        <Badge variant={classificationVariant(result.classification)} className="mt-5">
          {result.classification}
        </Badge>
        <p className="mt-4 max-w-lg text-[15px] leading-relaxed text-muted-foreground text-balance">
          {result.summary}
        </p>
      </section>

      <Separator className="my-10" />

      {/* Why? — dimensions */}
      <section className="space-y-5">
        <h2 className="font-display text-lg font-semibold tracking-tightish">Capability areas</h2>
        <div className="divide-y divide-border rounded-xl border border-border bg-card px-5">
          {result.dimension_results.map((d) => (
            <DimensionBar key={d.dimension} result={d} />
          ))}
        </div>
      </section>

      <div className="my-10 grid gap-5 sm:grid-cols-2">
        {/* Strengths */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Check className="h-4 w-4 text-success" /> Key strengths
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <ul className="space-y-2.5">
              {result.key_strengths.length ? (
                result.key_strengths.map((s, i) => (
                  <li key={i} className="flex gap-2.5 text-sm leading-relaxed text-foreground/90">
                    <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-success" />
                    {s}
                  </li>
                ))
              ) : (
                <li className="text-sm text-muted-foreground">Not enough evidence to highlight strengths.</li>
              )}
            </ul>
          </CardContent>
        </Card>

        {/* Development priorities */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <AlertTriangle className="h-4 w-4 text-warning" /> Development priorities
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <ul className="space-y-2.5">
              {result.capability_gaps.length ? (
                result.capability_gaps.map((g, i) => (
                  <li key={i} className="flex gap-2.5 text-sm leading-relaxed text-foreground/90">
                    <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-warning" />
                    {g}
                  </li>
                ))
              ) : (
                <li className="text-sm text-muted-foreground">No significant gaps identified.</li>
              )}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* What should I do next? — pathway */}
      <Card className="overflow-hidden">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-secondary text-foreground">
              <Compass className="h-5 w-5" />
            </div>
            <div className="space-y-2">
              <p className="text-xs font-medium uppercase tracking-[0.12em] text-muted-foreground">
                Recommended next step
              </p>
              <h3 className={`font-display text-xl font-semibold tracking-tightish ${PATHWAY_TONE[result.recommendation.pathway]}`}>
                {result.recommendation.pathway}
              </h3>
              <p className="max-w-xl text-sm leading-relaxed text-muted-foreground">
                {result.recommendation.rationale}
              </p>
              <p className="pt-1 text-sm font-medium text-foreground">
                Next: {result.recommendation.next_action}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="mt-10 flex items-center justify-between">
        <Button variant="ghost" asChild>
          <Link to="/app/assessments">All assessments</Link>
        </Button>
        <Button asChild className="group">
          <Link to={`/app/assessments/${id}/report`}>
            Read full report
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
        </Button>
      </div>
    </PageContainer>
  );
}
