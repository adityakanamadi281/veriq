import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Plus } from "lucide-react";
import { client } from "@/lib/client";
import { PageContainer, PageHeading } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/Feedback";
import { formatRelativeDate } from "@/lib/utils";

export function AssessmentHistory() {
  const { data: assessments, isLoading } = useQuery({
    queryKey: ["assessments"],
    queryFn: client.listAssessments,
  });

  return (
    <PageContainer className="max-w-3xl">
      <div className="flex items-start justify-between gap-4">
        <PageHeading
          eyebrow="Assessments"
          title="Your assessments"
          description="Each assessment is adaptive and evidence-led. Re-assess after developing your capabilities to see progress."
          className="mb-0"
        />
        <Button asChild className="mt-1 shrink-0 gap-1.5">
          <Link to="/app/assessments/new">
            <Plus className="h-4 w-4" /> New
          </Link>
        </Button>
      </div>

      <div className="mt-8 space-y-3">
        {isLoading ? (
          [0, 1, 2].map((i) => <Skeleton key={i} className="h-20 w-full rounded-xl" />)
        ) : assessments && assessments.length > 0 ? (
          assessments.map((a) => {
            const completed = a.status === "completed";
            return (
              <Link
                key={a.id}
                to={`/app/assessments/${a.id}${completed ? "/result" : ""}`}
                className="flex items-center justify-between rounded-xl border border-border bg-card p-5 transition-colors hover:bg-accent/50"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-foreground">
                      {completed ? "Completed" : "In progress"}
                    </span>
                    {completed && a.classification && (
                      <Badge variant="muted">{a.classification}</Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">{formatRelativeDate(a.created_at)}</p>
                </div>
                <div className="flex items-center gap-4">
                  {completed && a.overall_score != null && (
                    <span className="font-display text-xl font-semibold tabular-nums">{a.overall_score}</span>
                  )}
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>
              </Link>
            );
          })
        ) : (
          <EmptyState
            title="No assessments yet"
            description="Start your first AI readiness assessment. It takes about ten minutes."
            action={
              <Button asChild>
                <Link to="/app/assessments/new">Start assessment</Link>
              </Button>
            }
          />
        )}
      </div>
    </PageContainer>
  );
}
