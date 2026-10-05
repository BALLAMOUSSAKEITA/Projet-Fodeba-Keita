import Link from "next/link";
import type { ReactNode } from "react";

const baseClass =
  "inline-flex h-8 w-8 items-center justify-center rounded-lg border transition focus:outline-none focus:ring-2 focus:ring-teal-500/30";

const variants = {
  neutral: "border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900",
  primary: "border-teal-200 text-teal-700 hover:bg-teal-50",
  danger: "border-red-200 text-red-600 hover:bg-red-50",
};

function Svg({ children }: { children: ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-4 w-4"
      aria-hidden
    >
      {children}
    </svg>
  );
}

export function IconView() {
  return (
    <Svg>
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </Svg>
  );
}

export function IconEdit() {
  return (
    <Svg>
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5Z" />
    </Svg>
  );
}

export function IconTrash() {
  return (
    <Svg>
      <path d="M3 6h18" />
      <path d="M8 6V4h8v2" />
      <path d="M19 6v14H5V6" />
      <path d="M10 11v6M14 11v6" />
    </Svg>
  );
}

export function IconActionLink({
  href,
  label,
  variant = "primary",
  icon = "view",
}: {
  href: string;
  label: string;
  variant?: keyof typeof variants;
  icon?: "view" | "edit";
}) {
  return (
    <Link href={href} className={`${baseClass} ${variants[variant]}`} title={label} aria-label={label}>
      {icon === "edit" ? <IconEdit /> : <IconView />}
    </Link>
  );
}

export function IconActionButton({
  label,
  onClick,
  variant = "neutral",
  disabled,
  icon,
}: {
  label: string;
  onClick: () => void;
  variant?: keyof typeof variants;
  disabled?: boolean;
  icon: "edit" | "trash";
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`${baseClass} ${variants[variant]} disabled:cursor-not-allowed disabled:opacity-40`}
      title={label}
      aria-label={label}
    >
      {icon === "edit" ? <IconEdit /> : <IconTrash />}
    </button>
  );
}
