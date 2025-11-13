import { clsx } from "clsx";
import type { HTMLAttributes } from "react";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: "neutral" | "success" | "warning" | "danger" | "primary";
}

const toneMap: Record<NonNullable<BadgeProps["tone"]>, string> = {
  neutral: "bg-neutral-100 text-neutral-600",
  success: "bg-green-100 text-green-700",
  warning: "bg-yellow-100 text-yellow-700",
  danger: "bg-red-100 text-red-700",
  primary: "bg-primary-100 text-primary-700",
};

export function Badge({
  className,
  tone = "neutral",
  ...props
}: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold",
        toneMap[tone],
        className,
      )}
      {...props}
    />
  );
}

