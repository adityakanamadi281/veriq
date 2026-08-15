import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Printer } from "lucide-react";
import { client } from "@/lib/client";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScoreRing } from "@/components/ScoreRing";
import { DimensionBar } from "@/components/DimensionBar";
import { ProcessingState } from "@/components/ProcessingState";
import { ErrorState } from "@/components/Feedback";
import { classificationVariant } from "@/lib/classification";
import { cn, formatRelativeDate } from "@/lib/utils";

const sections = [
  { id: "summary", label: "Summary" },
  { id: "readiness", label: "Readiness" },
  { id: "strengths", label: "Strengths" },
  { id: "development", label: "Development Areas" },
  { id: "evidence", label: "Evidence" },
  { id: "pathway", label: "Recommended Pathway" },
  { id: "priorities", label: "Learning Priorities" },
];

export function ReportPage() {
  const { id } = useParams();
  const { data: report, isLoading, isError, refetch } = useQuery({
    queryKey: ["report", id],
    queryFn: () => client.getReport(id!),
    enabled: !!id,
  });

  if (isLoading) return <PageContainer><ProcessingState label="Loading your report" /></PageContainer>;
  if (isError) return <PageContainer><ErrorState message="We couldn’t load your report." onRetry={() => refetch()} /></PageContainer>;
  if (!report) return null;

  return (
    <div className="container max-w-5xl py-10 sm:py-14 animate-fade-in">
      {/* Document header */}
      <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-1.5">
          <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground">
            {formatRelativeDate(report.created_at)}
          </p>
          <h1 className="font-display text-2xl font-semibold tracking-tightish sm:text-[28px]">
            {report.title}
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => window.print()} className="gap-1.5">
            <Printer className="h-4 w-4" /> Save / Print
          </Button>
          <Button variant="ghost" size="sm" asChild className="gap-1.5">
            <Link to={`/app/assessments/${id}/result`}>
              <ArrowLeft className="h-4 w-4" /> Result
            </Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-10 sm:grid-cols-[200px_1fr]">
        {/* Section index */}
        <nav className="hidden sm:block">
          <div className="sticky top-24 space-y-1">
            <p className="mb-2 text-xs font-medium uppercase tracking-[0.12em] text-muted-foreground">
              Contents
            </p>
            {sections.map((s) => (
              <a
                key={s.id}
                href={`#${s.id}`}
                className="block rounded-md px-2.5 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              >
                {s.label}
              </a>
            ))}
          </div>
        </nav>

        {/* Document body */}
        <article className="max-w-2xl space-y-12">
          <Section id="summary" title="Summary">
            <p className="text-[15px] leading-relaxed text-foreground/90">{report.summary}</p>
          </Section>

          <Section id="readiness" title="Readiness">
            <div className="flex flex-col items-center gap-5 rounded-xl border border-border bg-card p-6 sm:flex-row sm:items-center sm:gap-8">
              <ScoreRing score={report.readiness.overall_score} size={140} />
              <div className="space-y-2 text-center sm:text-left">
                <Badge variant={classificationVariant(report.readiness.classification)}>
                  {report.readiness.classification}
                </Badge>
                <p className="text-sm text-muted-foreground">
                  Overall readiness across six assessed capability areas.
                </p>
              </div>
            </div>
            <div className="mt-6 divide-y divide-border rounded-xl border border-border bg-card px-5">
              {report.readiness.dimensions.map((d) => (
                <DimensionBar key={d.dimension} result={d} />
              ))}
            </div>
          </Section>

          <Section id="strengths" title="Strengths">
            <FindingsList items={report.strengths} tone="success" empty="No specific strengths recorded." />
          </Section>

          <Section id="development" title="Development Areas">
            <FindingsList items={report.development_areas} tone="warning" empty="No development areas recorded." />
          </Section>

          <Section id="evidence" title="Evidence">
            {report.evidence.length ? (
              <ul className="space-y-3">
                {report.evidence.map((e, i) => (
                  <li key={i} className="rounded-lg border border-border bg-card/60 p-4">
                    <p className="text-sm leading-relaxed text-foreground/90">{e.statement}</p>
                    <p className="mt-1.5 text-xs text-muted-foreground">Supports: {e.supports}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground">No evidence recorded.</p>
            )}
          </Section>

          <Section id="pathway" title="Recommended Pathway">
            <div className="rounded-xl border border-border bg-card p-6">
              <h3 className="font-display text-lg font-semibold tracking-tightish">
                {report.recommended_pathway.pathway}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {report.recommended_pathway.rationale}
              </p>
              {report.recommended_pathway.capability_areas.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {report.recommended_pathway.capability_areas.map((c) => (
                    <Badge key={c} variant="muted">{c}</Badge>
                  ))}
                </div>
              )}
              <Separator className="my-4" />
              <p className="text-sm font-medium text-foreground">
                Next: {report.recommended_pathway.next_action}
              </p>
            </div>
          </Section>

          <Section id="priorities" title="Learning Priorities">
            <ol className="space-y-2.5">
              {report.learning_priorities.map((p, i) => (
                <li key={i} className="flex gap-3 text-sm leading-relaxed text-foreground/90">
                  <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-secondary text-xs font-medium text-foreground">
                    {i + 1}
                  </span>
                  {p}
                </li>
              ))}
            </ol>
          </Section>
        </article>
      </div>
    </div>
  );
}

function Section({ id, title, children }: { id: string; title: string; children: React.ReactNode }) {
  return (
    <section id={id} className="scroll-mt-24 space-y-4">
      <h2 className="font-display text-lg font-semibold tracking-tightish">{title}</h2>
      {children}
    </section>
  );
}

function FindingsList({
  items,
  tone,
  empty,
}: {
  items: string[];
  tone: "success" | "warning";
  empty: string;
}) {
  if (!items.length) return <p className="text-sm text-muted-foreground">{empty}</p>;
  return (
    <ul className="space-y-2.5">
      {items.map((s, i) => (
        <li key={i} className="flex gap-2.5 text-sm leading-relaxed text-foreground/90">
          <span className={cn("mt-2 h-1 w-1 shrink-0 rounded-full", tone === "success" ? "bg-success" : "bg-warning")} />
          {s}
        </li>
      ))}
    </ul>
  );
}
