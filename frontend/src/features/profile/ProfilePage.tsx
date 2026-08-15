import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Upload, FileCheck2, Plus, Trash2 } from "lucide-react";
import { client } from "@/lib/client";
import { ApiRequestError } from "@/lib/api";
import { PageContainer, PageHeading } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { TagInput } from "@/components/ui/tag-input";
import { Separator } from "@/components/ui/separator";
import { ErrorState } from "@/components/Feedback";
import type { Profile, Project } from "@/types";

const empty: Profile = {
  user_id: "",
  name: "",
  education: "",
  graduation_year: null,
  experience: "",
  target_role: "",
  technical_skills: [],
  projects: [],
  ai_tools: [],
  github: "",
  linkedin: "",
  professional_links: [],
  background: "",
  resume_parsed: false,
  resume_path: null,
};

export function ProfilePage() {
  const qc = useQueryClient();
  const { data: profile, isError, refetch } = useQuery({
    queryKey: ["profile"],
    queryFn: client.getProfile,
  });

  const [form, setForm] = useState<Profile>(empty);
  const [synced, setSynced] = useState(false);

  // Sync server profile into local form once loaded.
  if (profile && !synced) {
    setForm({ ...empty, ...profile });
    setSynced(true);
  }

  const saveMutation = useMutation({
    mutationFn: (data: Partial<Profile>) => client.updateProfile(data),
    onSuccess: () => {
      toast.success("Profile saved");
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Could not save profile"),
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => client.uploadResume(file),
    onSuccess: (res) => {
      setForm({ ...empty, ...res.profile });
      toast.success(
        res.extracted_fields.length
          ? `Extracted ${res.extracted_fields.length} field${res.extracted_fields.length > 1 ? "s" : ""} from your CV. Review and save.`
          : "CV uploaded. Review your profile and save."
      );
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
    onError: (err) =>
      toast.error(err instanceof ApiRequestError ? err.message : "Could not upload your CV."),
  });

  function set<K extends keyof Profile>(key: K, value: Profile[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function handleSave() {
    saveMutation.mutate({
      name: form.name,
      education: form.education,
      graduation_year: form.graduation_year,
      experience: form.experience,
      target_role: form.target_role,
      technical_skills: form.technical_skills,
      projects: form.projects,
      ai_tools: form.ai_tools,
      github: form.github,
      linkedin: form.linkedin,
      professional_links: form.professional_links,
      background: form.background,
    });
  }

  if (isError) return <PageContainer><ErrorState message="We couldn’t load your profile." onRetry={() => refetch()} /></PageContainer>;

  return (
    <PageContainer className="max-w-3xl">
      <PageHeading
        eyebrow="Profile"
        title="Help us understand you before we begin"
        description="This context shapes how the assessment adapts. Where information can come from your CV, upload it and review the extracted fields — no need to re-enter them."
      />

      {/* Resume upload */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>CV / Resume</CardTitle>
          <CardDescription>Upload a PDF. We’ll extract the details for you to confirm.</CardDescription>
        </CardHeader>
        <CardContent>
          {form.resume_parsed ? (
            <div className="flex items-center justify-between rounded-lg border border-border bg-background/60 px-4 py-3.5">
              <div className="flex items-center gap-3">
                <FileCheck2 className="h-5 w-5 text-success" />
                <div>
                  <p className="text-sm font-medium text-foreground">CV on file</p>
                  <p className="text-xs text-muted-foreground">Extracted fields are filled in below — review and edit.</p>
                </div>
              </div>
              <ResumeUploader onFile={(f) => uploadMutation.mutate(f)} loading={uploadMutation.isPending}>
                Replace
              </ResumeUploader>
            </div>
          ) : (
            <ResumeUploader onFile={(f) => uploadMutation.mutate(f)} loading={uploadMutation.isPending} />
          )}
        </CardContent>
      </Card>

      <div className="space-y-8">
        <Section title="About you">
          <Field label="Name">
            <Input value={form.name || ""} onChange={(e) => set("name", e.target.value)} placeholder="Your name" />
          </Field>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Education">
              <Input value={form.education || ""} onChange={(e) => set("education", e.target.value)} placeholder="e.g. B.Tech, Computer Science" />
            </Field>
            <Field label="Graduation year">
              <Input
                type="number"
                value={form.graduation_year ?? ""}
                onChange={(e) => set("graduation_year", e.target.value ? Number(e.target.value) : null)}
                placeholder="e.g. 2025"
              />
            </Field>
          </div>
          <Field label="Target role" hint="The AI-first engineering role you’re aiming for.">
            <Input value={form.target_role || ""} onChange={(e) => set("target_role", e.target.value)} placeholder="e.g. Backend Engineer, AI Engineer" />
          </Field>
          <Field label="Experience" hint="Years or a short description of where you are.">
            <Input value={form.experience || ""} onChange={(e) => set("experience", e.target.value)} placeholder="e.g. 2 years, mid-level" />
          </Field>
          <Field label="Professional background" hint="A short paragraph — what you’ve built and what you’re good at.">
            <Textarea value={form.background || ""} onChange={(e) => set("background", e.target.value)} placeholder="Tell us briefly about your background." />
          </Field>
        </Section>

        <Separator />

        <Section title="Skills & tools">
          <TagInput
            label="Technical skills"
            values={form.technical_skills}
            onChange={(v) => set("technical_skills", v)}
            placeholder="Type a skill and press Enter"
          />
          <TagInput
            label="AI / coding tools you use"
            values={form.ai_tools}
            onChange={(v) => set("ai_tools", v)}
            placeholder="e.g. Copilot, Cursor, Claude Code"
          />
        </Section>

        <Separator />

        <Section title="Links">
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="GitHub">
              <Input value={form.github || ""} onChange={(e) => set("github", e.target.value)} placeholder="https://github.com/you" />
            </Field>
            <Field label="LinkedIn">
              <Input value={form.linkedin || ""} onChange={(e) => set("linkedin", e.target.value)} placeholder="https://linkedin.com/in/you" />
            </Field>
          </div>
          <TagInput
            label="Other professional links"
            values={form.professional_links}
            onChange={(v) => set("professional_links", v)}
            placeholder="Portfolio, blog, etc."
          />
        </Section>

        <Separator />

        <Section title="Projects">
          <ProjectEditor projects={form.projects} onChange={(v) => set("projects", v)} />
        </Section>
      </div>

      <div className="mt-10 flex items-center justify-end gap-3">
        <Button variant="outline" onClick={() => profile && setForm({ ...empty, ...profile })}>
          Reset
        </Button>
        <Button onClick={handleSave} disabled={saveMutation.isPending}>
          {saveMutation.isPending ? "Saving…" : "Save profile"}
        </Button>
      </div>
    </PageContainer>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-4">
      <h2 className="font-display text-base font-semibold tracking-tightish">{title}</h2>
      {children}
    </section>
  );
}

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      {children}
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}

function ProjectEditor({ projects, onChange }: { projects: Project[]; onChange: (p: Project[]) => void }) {
  function add() {
    onChange([...projects, { name: "", description: "", technologies: [] }]);
  }
  function update(i: number, patch: Partial<Project>) {
    onChange(projects.map((p, idx) => (idx === i ? { ...p, ...patch } : p)));
  }
  function remove(i: number) {
    onChange(projects.filter((_, idx) => idx !== i));
  }

  return (
    <div className="space-y-3">
      {projects.map((p, i) => (
        <div key={i} className="rounded-lg border border-border bg-background/60 p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium uppercase tracking-[0.1em] text-muted-foreground">
              Project {i + 1}
            </span>
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => remove(i)} aria-label="Remove project">
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
          <div className="mt-3 grid gap-3">
            <Input value={p.name} onChange={(e) => update(i, { name: e.target.value })} placeholder="Project name" />
            <Textarea
              className="min-h-[72px]"
              value={p.description}
              onChange={(e) => update(i, { description: e.target.value })}
              placeholder="What it does and your role"
            />
            <TagInput
              values={p.technologies || []}
              onChange={(v) => update(i, { technologies: v })}
              placeholder="Technologies used"
            />
          </div>
        </div>
      ))}
      <Button variant="outline" size="sm" onClick={add} className="gap-1.5">
        <Plus className="h-4 w-4" /> Add project
      </Button>
    </div>
  );
}

function ResumeUploader({
  onFile,
  loading,
  children,
}: {
  onFile: (file: File) => void;
  loading: boolean;
  children?: React.ReactNode;
}) {
  return (
    <label
      className="flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-border bg-background/40 px-6 py-8 text-center transition-colors hover:bg-accent/40"
    >
      <Upload className="h-5 w-5 text-muted-foreground" />
      <span className="mt-2.5 text-sm font-medium text-foreground">
        {loading ? "Processing…" : children || "Click to upload a PDF resume"}
      </span>
      <span className="mt-0.5 text-xs text-muted-foreground">PDF, up to 5 MB</span>
      <input
        type="file"
        accept="application/pdf,.pdf"
        className="hidden"
        disabled={loading}
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) onFile(f);
          e.target.value = "";
        }}
      />
    </label>
  );
}
