import type { ReactNode } from "react";
import type { NavIconName } from "@/lib/navigation";

type Props = {
  name: NavIconName;
  className?: string;
};

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
      <path d="M16 11h5M18.5 8.5v5" />
    </>
  ),
  roles: (
    <>
      <rect x="5" y="11" width="14" height="10" rx="2" />
      <path d="M12 11V7a3 3 0 0 1 6 0v1" />
    </>
  ),
  students: (
    <>
      <path d="M12 3 4 7v6c0 4.4 3.6 8 8 8s8-3.6 8-8V7l-8-4Z" />
      <path d="M12 11v6M9 14h6" />
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
      <path d="M18 8h3v3" />
    </>
  ),
  calendar: (
    <>
      <rect x="4" y="5" width="16" height="16" rx="2" />
      <path d="M8 3v4M16 3v4M4 10h16" />
    </>
  ),
  grades: (
    <>
      <path d="M7 4h10v16H7z" />
      <path d="M10 9h6M10 13h6M10 17h4" />
    </>
  ),
  "reports-card": (
    <>
      <path d="M6 4h12v16H6z" />
      <path d="M9 9h6M9 13h6M9 17h4" />
    </>
  ),
  attendance: (
    <>
      <path d="M5 12 10 17 19 7" />
    </>
  ),
  finance: (
    <>
      <rect x="3" y="7" width="18" height="12" rx="2" />
      <path d="M3 11h18M7 15h2" />
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
      <path d="M9 8h6M9 12h6M9 16h4" />
    </>
  ),
  analytics: (
    <>
      <path d="M4 19V9M10 19V5M16 19v-7M22 19V3" />
    </>
  ),
  security: (
    <>
      <path d="M12 3 5 7v6c0 4.4 3.6 8 7 8s7-3.6 7-8V7l-7-4Z" />
      <path d="M10 12 12 14 16 10" />
    </>
  ),
  announcements: (
    <>
      <path d="M5 10v4c0 1.1.9 2 2 2h1l4 4V4L8 8H7c-1.1 0-2 .9-2 2Z" />
      <path d="M17 9a4 4 0 0 1 0 6" />
    </>
  ),
  portal: (
    <>
      <circle cx="9" cy="9" r="2.5" />
      <circle cx="15" cy="9" r="2.5" />
      <path d="M4 19c0-2.8 2.2-5 5-5s5 2.2 5 5M14 19c0-2.2 1.8-4 4-4" />
    </>
  ),
  settings: (
    <>
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v2M12 20v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M2 12h2M20 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4" />
    </>
  ),
};

export function NavIcon({ name, className = "h-[18px] w-[18px]" }: Props) {
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
