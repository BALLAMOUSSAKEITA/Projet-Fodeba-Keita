import type { ReactNode } from "react";
import type { NavIconName } from "@/lib/navigation";

const paths: Record<NavIconName, ReactNode> = {
  dashboard: (
    <>
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </>
  ),
  users: (
    <>
      <circle cx="9" cy="8" r="3" />
      <path d="M3 19c0-3.3 2.7-6 6-6s6 2.7 6 6" />
    </>
  ),
  students: (
    <>
      <path d="M12 3 4 7v6c0 4.4 3.6 8 8 8s8-3.6 8-8V7l-8-4Z" />
      <path d="M9 14h6" />
    </>
  ),
  classes: (
    <>
      <path d="M3 10 12 5l9 5-9 5-9-5Z" />
      <path d="M6 12v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5" />
    </>
  ),
  staff: (
    <>
      <circle cx="12" cy="8" r="3" />
      <path d="M6 20c0-3.3 2.7-6 6-6s6 2.7 6 6" />
    </>
  ),
  calendar: (
    <>
      <rect x="4" y="5" width="16" height="16" rx="2" />
      <path d="M8 3v4M16 3v4M4 10h16" />
    </>
  ),
  finance: (
    <>
      <rect x="3" y="7" width="18" height="12" rx="2" />
      <path d="M3 11h18" />
    </>
  ),
  payroll: (
    <>
      <rect x="4" y="6" width="16" height="14" rx="2" />
      <path d="M8 10h8M8 14h5" />
    </>
  ),
  ledger: (
    <>
      <path d="M5 4h14v16H5z" />
      <path d="M9 8h6M9 12h6" />
    </>
  ),
  analytics: <path d="M4 19V9M10 19V5M16 19v-7M22 19V3" />,
};

export function NavIcon({ name, className = "h-[18px] w-[18px]" }: { name: NavIconName; className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden
    >
      {paths[name]}
    </svg>
  );
}
