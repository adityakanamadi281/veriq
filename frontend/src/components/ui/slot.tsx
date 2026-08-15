import * as React from "react";

/**
 * Minimal Slot implementation (subset of @radix-ui/react-slot) so components
 * can render as their child element via `asChild` without a dependency.
 */
interface SlotProps extends React.HTMLAttributes<HTMLElement> {
  children?: React.ReactNode;
}

export const Slot = React.forwardRef<HTMLElement, SlotProps>(
  ({ children, ...props }, ref) => {
    if (React.isValidElement(children)) {
      const child = children as React.ReactElement<Record<string, unknown>>;
      return React.cloneElement(child, {
        ...mergeProps(props, child.props),
        ref: mergeRefs(ref, (child as unknown as { ref?: React.Ref<HTMLElement> }).ref),
      }) as React.ReactElement;
    }
    return null;
  }
);
Slot.displayName = "Slot";

function mergeProps(
  slotProps: Record<string, unknown>,
  childProps: Record<string, unknown>
): Record<string, unknown> {
  const merged: Record<string, unknown> = { ...childProps };
  for (const key in slotProps) {
    const slotValue = slotProps[key];
    const childValue = childProps[key];
    if (key === "className") {
      merged[key] = [slotValue, childValue].filter(Boolean).join(" ");
    } else if (key.startsWith("on") && typeof slotValue === "function" && typeof childValue === "function") {
      merged[key] = (...args: unknown[]) => {
        childValue(...args);
        slotValue(...args);
      };
    } else if (childValue === undefined) {
      merged[key] = slotValue;
    }
  }
  return merged;
}

function mergeRefs<T>(...refs: (React.Ref<T> | undefined)[]): React.Ref<T> {
  return (node: T) => {
    for (const ref of refs) {
      if (typeof ref === "function") ref(node);
      else if (ref && "current" in ref) (ref as React.MutableRefObject<T>).current = node;
    }
  };
}
