import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { client } from "@/lib/client";
import { ApiRequestError } from "@/lib/api";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { ProcessingState } from "@/components/ProcessingState";
import { ErrorState } from "@/components/Feedback";
import { cn } from "@/lib/utils";
import type { Question } from "@/types";

const FORMAT_LABELS: Record<string, string> = {
  written: "Written response",
  scenario: "Scenario",
  multiple_choice: "Choose one",
  code_review: "Code review",
  debugging: "Debugging",
  practical_reasoning: "Practical reasoning",
  agent_instruction: "Agent instruction",
};

export function AssessmentRunner() {
  const { id } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data: state, isLoading, isError, refetch } = useQuery({
    queryKey: ["assessment", id],
    queryFn: () => client.getAssessment(id!),
    enabled: !!id,
  });

  const submit = useMutation({
    mutationFn: (vars: { question_id: string; text: string; selected_option_id?: string; submission_key: string }) =>
      client.submitResponse(id!, vars),
    onSuccess: (next) => {
      qc.setQueryData(["assessment", id], next);
      if (next.status === "completed") {
        navigate(`/app/assessments/${id}/result`);
      }
    },
    onError: (err) =>
      toast.error(err instanceof ApiRequestError ? err.message : "Could not submit your response. Try again."),
  });

  // Calm, professional processing overlay while the backend evaluates.
  const [phase, setPhase] = useState<"idle" | "evaluating" | "preparing">("idle");
  useEffect(() => {
    if (!submit.isPending) {
      setPhase("idle");
      return;
    }
    setPhase("evaluating");
    const t = setTimeout(() => setPhase("preparing"), 1300);
    return () => clearTimeout(t);
  }, [submit.isPending]);

  if (isLoading) return <PageContainer><ProcessingState label="Loading assessment" /></PageContainer>;
  if (isError) return <PageContainer><ErrorState message="We couldn’t load this assessment." onRetry={() => refetch()} /></PageContainer>;
  if (!state) return null;

  if (state.status === "completed") {
    navigate(`/app/assessments/${id}/result`, { replace: true });
    return null;
  }

  const question = state.current_question;

  return (
    <div className="container max-w-2xl py-10 sm:py-14">
      {/* Restrained progress — count, not a fake percentage. */}
      <div className="mb-10 space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground">
            Assessment
          </span>
          <span className="text-xs text-muted-foreground tabular-nums">
            Question {state.answered_count + (question ? 1 : 0)} of up to {state.max_questions}
          </span>
        </div>
        <Progress value={state.answered_count} max={state.max_questions} />
      </div>

      {question ? (
        <QuestionCard
          key={question.id}
          question={question}
          disabled={submit.isPending}
          onSubmit={(text, selected) =>
            submit.mutate({
              question_id: question.id,
              text,
              selected_option_id: selected,
              submission_key: crypto.randomUUID(),
            })
          }
        />
      ) : (
        <ProcessingState
          label={state.processing_label || "Preparing your assessment"}
          description="Reviewing your responses across the assessed capability areas."
        />
      )}

      {submit.isPending && (
        <ProcessingState
          className="mt-10 border-t border-border pt-10"
          label={phase === "evaluating" ? "Evaluating response" : "Preparing next question"}
          description={
            phase === "evaluating"
              ? "Reviewing your answer against the assessment criteria."
              : "Selecting the next highest-value question for you."
          }
        />
      )}
    </div>
  );
}

function QuestionCard({
  question,
  disabled,
  onSubmit,
}: {
  question: Question;
  disabled: boolean;
  onSubmit: (text: string, selected?: string) => void;
}) {
  const [text, setText] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const isChoice = question.format === "multiple_choice" && question.options.length > 0;

  function submit() {
    if (isChoice) {
      if (!selected) return;
      onSubmit("", selected);
    } else {
      if (!text.trim()) return;
      onSubmit(text.trim());
    }
  }

  const canSubmit = isChoice ? Boolean(selected) : text.trim().length > 0;

  return (
    <div className="animate-fade-in">
      <div className="mb-5 flex items-center gap-2">
        <Badge variant="secondary">{question.dimension}</Badge>
        <Badge variant="muted">{FORMAT_LABELS[question.format] || question.format}</Badge>
      </div>

      <h1 className="font-display text-xl font-semibold leading-snug tracking-tightish text-balance sm:text-2xl">
        {question.prompt}
      </h1>

      {question.context && (
        <pre className="mt-5 overflow-x-auto rounded-lg border border-border bg-muted/50 p-4 text-[13px] leading-relaxed text-foreground/90">
          <code>{question.context}</code>
        </pre>
      )}

      <div className="mt-6">
        {isChoice ? (
          <div className="space-y-2.5">
            {question.options.map((opt) => (
              <button
                key={opt.id}
                type="button"
                disabled={disabled}
                onClick={() => setSelected(opt.id)}
                className={cn(
                  "flex w-full items-start gap-3 rounded-lg border bg-card px-4 py-3.5 text-left text-sm transition-all",
                  selected === opt.id
                    ? "border-foreground ring-1 ring-foreground"
                    : "border-border hover:bg-accent/50"
                )}
              >
                <span
                  className={cn(
                    "mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full border",
                    selected === opt.id ? "border-foreground bg-foreground" : "border-border"
                  )}
                >
                  {selected === opt.id && <span className="h-1.5 w-1.5 rounded-full bg-primary-foreground" />}
                </span>
                <span className="text-foreground">{opt.text}</span>
              </button>
            ))}
          </div>
        ) : (
          <>
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={disabled}
              placeholder="Type your answer…"
              className="min-h-[160px]"
              autoFocus
            />
          </>
        )}
      </div>

      <div className="mt-6 flex items-center justify-between">
        <span className="text-xs text-muted-foreground">
          {isChoice ? "Select one option to continue." : "Take your time — depth matters more than length."}
        </span>
        <Button onClick={submit} disabled={disabled || !canSubmit}>
          Continue
        </Button>
      </div>
    </div>
  );
}
