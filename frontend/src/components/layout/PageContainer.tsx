import { cn } from "@/lib/utils";

export function PageContainer({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={cn("container max-w-3xl py-10 sm:py-16 animate-fade-in", className)}>
      {children}
    </div>
  );
}

export function PageHeading({
  eyebrow,
  title,
  description,
  className,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  className?: string;
}) {
  return (
    <div className={cn("mb-8 space-y-3", className)}>
      {eyebrow && (
        <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground">
          {eyebrow}
        </p>
      )}
      <h1 className="font-display text-2xl font-semibold tracking-tightish text-balance sm:text-[28px]">
        {title}
      </h1>
      {description && (
        <p className="max-w-xl text-[15px] leading-relaxed text-muted-foreground">{description}</p>
      )}
    </div>
  );
}
