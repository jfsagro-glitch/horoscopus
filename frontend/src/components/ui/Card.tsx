import { clsx } from "clsx";
import type { HTMLAttributes } from "react";

export function Card({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={clsx(
        "rounded-2xl border border-neutral-200 bg-white/80 p-6 shadow-sm backdrop-blur",
        className,
      )}
      {...props}
    />
  );
}

