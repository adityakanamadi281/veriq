import { Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, FileText, Sparkles } from "lucide-react";
import { client } from "@/lib/client";
import { useAuth } from "@/context/AuthContext";
import { PageContainer, PageHeading } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/Feedback";
import { formatRelativeDate } from "@/lib/utils";

export function Home() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: client.getProfile,
  });

  const { data: assessments } = useQuery({
    queryKey: ["assessments"],
    queryFn: client.listAssessments,
  });

  const latest = assessments?.[0];
  const hasCompleted = latest?.status === "completed";

  const profileReady = Boolean(profile && (profile.target_role || profile.background || profile.resume_parsed));

  function startAssessment() {
    if (!profileReady) {
      navigate("/app/profile");
    } else {
      navigate("/app/assessments");
    }
  }

  return (
    <PageContainer className="max-w-3xl">
      <PageHeading
        eyebrow="Home"
        title={user?.email ? `Welcome back` : "Welcome"}
        description="VERIQ understands your background, runs an adaptive assessment, and gives you an evidence-based view of your readiness."
      />

      <div className="rounded-xl border border-border bg-card p-6 shadow-[0_1px_2px_0_hsl(var(--foreground)/0.04)]">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <h2 className="font-display text-lg font-semibold tracking-tightish">Start your assessment</h2>
              {!profileReady && <Badge variant="muted">Profile needed</Badge>}
            </div>
            <p className="max-w-md text-sm leading-relaxed text-muted-foreground">
              {profileReady
                ? "Your profile is ready. The assessment adapts to your background and previous answers."
                : "Add a target role or upload your CV first so the assessment can adapt to you."}
            </p>
          </div>
          <Button size="lg" onClick={startAssessment} className="group shrink-0">
            <Sparkles className="h-4 w-4" />
            Start Assessment
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Button>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <ProfileStat label="Target role" value={profile?.target_role || "—"} loading={profileLoading} />
          <ProfileStat
            label="Skills"
            value={profile?.technical_skills?.length ? `${profile.technical_skills.length}` : "—"}
            loading={profileLoading}
          />
          <ProfileStat label="CV" value={profile?.resume_parsed ? "Uploaded" : "—"} loading={profileLoading} />
          <ProfileStat
            label="Assessments"
            value={assessments ? `${assessments.length}` : "—"}
            loading={profileLoading}
          />
        </div>
      </div>

      <div className="mt-8">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="font-display text-base font-semibold tracking-tightish">Most recent assessment</h3>
          {assessments && assessments.length > 0 && (
            <Link to="/app/assessments" className="text-sm text-muted-foreground hover:text-foreground">
              View all
            </Link>
          )}
        </div>
        {profileLoading ? (
          <Skeleton className="h-24 w-full rounded-xl" />
        ) : latest ? (
          <Link
            to={`/app/assessments/${latest.id}${hasCompleted ? "/result" : ""}`}
            className="flex items-center justify-between rounded-xl border border-border bg-card p-5 transition-colors hover:bg-accent/50"
          >
            <div className="space-y-1">
              <p className="text-sm font-medium text-foreground">
                {hasCompleted ? "Completed assessment" : "Assessment in progress"}
              </p>
              <p className="text-xs text-muted-foreground">{formatRelativeDate(latest.created_at)}</p>
            </div>
            <div className="flex items-center gap-4">
              {hasCompleted && latest.overall_score != null && (
                <span className="font-display text-2xl font-semibold tabular-nums">{latest.overall_score}</span>
              )}
              {hasCompleted && (
                <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
                  <FileText className="h-4 w-4" /> Report
                </span>
              )}
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </div>
          </Link>
        ) : (
          <EmptyState
            title="No assessments yet"
            description="When you complete an assessment, your most recent result will appear here."
          />
        )}
      </div>
    </PageContainer>
  );
}

function ProfileStat({ label, value, loading }: { label: string; value: string; loading: boolean }) {
  return (
    <div className="rounded-lg border border-border bg-background/60 px-3.5 py-3">
      <p className="text-[11px] font-medium uppercase tracking-[0.1em] text-muted-foreground">{label}</p>
      <p className="mt-1 truncate text-sm font-medium text-foreground">
        {loading ? <Skeleton className="h-4 w-16" /> : value}
      </p>
    </div>
  );
}
