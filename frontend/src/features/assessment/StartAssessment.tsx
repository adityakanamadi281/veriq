import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Mic, MicOff, Keyboard } from "lucide-react";
import { client } from "@/lib/client";
import { ApiRequestError } from "@/lib/api";
import { PageContainer, PageHeading } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ProcessingState } from "@/components/ProcessingState";
import { cn } from "@/lib/utils";

// Minimal typing for the Web Speech API (not in lib.dom by default).
interface SpeechRecognitionResult {
  transcript: string;
}
interface SpeechRecognitionEvent {
  results: SpeechRecognitionResult[][];
}
interface SpeechRecognitionLike {
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((e: SpeechRecognitionEvent) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
  lang: string;
  interimResults: boolean;
  continuous: boolean;
}

function getSpeechRecognition(): { new (): SpeechRecognitionLike } | null {
  const w = window as unknown as {
    SpeechRecognition?: { new (): SpeechRecognitionLike };
    webkitSpeechRecognition?: { new (): SpeechRecognitionLike };
  };
  return w.SpeechRecognition || w.webkitSpeechRecognition || null;
}

export function StartAssessment() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"voice" | "type">("voice");
  const [text, setText] = useState("");
  const [recording, setRecording] = useState(false);
  const recRef = useRef<SpeechRecognitionLike | null>(null);
  const speechSupported = Boolean(getSpeechRecognition());

  const start = useMutation({
    mutationFn: (introduction: string) => client.startAssessment(introduction || undefined),
    onSuccess: (state) => navigate(`/app/assessments/${state.id}`),
    onError: (err) =>
      toast.error(err instanceof ApiRequestError ? err.message : "Could not start the assessment."),
  });

  useEffect(() => {
    return () => recRef.current?.abort();
  }, []);

  function toggleRecording() {
    const Ctor = getSpeechRecognition();
    if (!Ctor) {
      setMode("type");
      return;
    }
    if (recording) {
      recRef.current?.stop();
      setRecording(false);
      return;
    }
    const rec = new Ctor();
    rec.lang = "en-US";
    rec.interimResults = true;
    rec.continuous = true;
    let finalText = text;
    rec.onresult = (e) => {
      let interim = "";
      for (let i = 0; i < e.results.length; i++) {
        const r = e.results[i];
        const transcript = r[0].transcript;
        finalText = finalText + transcript;
        finalText = finalText.replace(interim, "");
        interim = transcript;
      }
      setText(finalText.trim());
    };
    rec.onend = () => setRecording(false);
    rec.onerror = () => {
      setRecording(false);
      toast.error("Voice input stopped. You can type instead.");
    };
    recRef.current = rec;
    setRecording(true);
    rec.start();
  }

  if (start.isPending) {
    return <PageContainer><ProcessingState label="Preparing your assessment" description="Setting up your adaptive assessment." /></PageContainer>;
  }

  return (
    <PageContainer className="max-w-2xl">
      <PageHeading
        eyebrow="Assessment"
        title="Introduce yourself"
        description="Tell us what you have built, what you are good at, and the kind of engineering work you want to do."
      />

      <div className="mb-5 inline-flex items-center gap-1 rounded-lg border border-border bg-muted/60 p-1">
        <button
          type="button"
          onClick={() => setMode("voice")}
          className={cn(
            "inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
            mode === "voice" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
          )}
        >
          <Mic className="h-4 w-4" /> Speak
        </button>
        <button
          type="button"
          onClick={() => {
            if (recording) toggleRecording();
            setMode("type");
          }}
          className={cn(
            "inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
            mode === "type" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
          )}
        >
          <Keyboard className="h-4 w-4" /> Type instead
        </button>
      </div>

      {mode === "voice" && speechSupported ? (
        <div className="space-y-4">
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border bg-card/50 py-12">
            <button
              type="button"
              onClick={toggleRecording}
              className={cn(
                "flex h-14 w-14 items-center justify-center rounded-full border transition-colors",
                recording
                  ? "border-danger bg-danger/10 text-danger"
                  : "border-border bg-secondary text-foreground hover:bg-accent"
              )}
              aria-label={recording ? "Stop recording" : "Start recording"}
            >
              {recording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
            </button>
            <p className="mt-4 text-sm font-medium text-foreground">
              {recording ? "Listening… tap to stop" : "Tap to speak"}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">Your speech is transcribed below.</p>
          </div>
          <Textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Your introduction will appear here. You can edit it." className="min-h-[140px]" />
        </div>
      ) : (
        <Textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Tell us what you’ve built, what you’re good at, and the work you want to do."
          className="min-h-[180px]"
          autoFocus
        />
      )}

      {mode === "voice" && !speechSupported && (
        <p className="mt-3 text-xs text-muted-foreground">Voice input isn’t supported in this browser — typing works just as well.</p>
      )}

      <div className="mt-8 flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate("/app/assessments")}>
          Back
        </Button>
        <Button onClick={() => start.mutate(text)} disabled={!text.trim()}>
          Begin assessment
        </Button>
      </div>
    </PageContainer>
  );
}
