import { Toaster as SonnerToaster } from "sonner";

export function Toaster() {
  return (
    <SonnerToaster
      position="bottom-right"
      toastOptions={{
        unstyled: false,
        classNames: {
          toast:
            "rounded-lg border border-border bg-card text-card-foreground shadow-[0_4px_24px_-6px_hsl(var(--foreground)/0.18)] text-sm",
          title: "font-medium text-foreground",
          description: "text-muted-foreground",
        },
      }}
      closeButton
      richColors={false}
    />
  );
}
