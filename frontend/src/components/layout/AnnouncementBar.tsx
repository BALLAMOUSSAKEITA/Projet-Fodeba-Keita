"use client";

type AnnouncementBarProps = {
  message?: string;
  href?: string;
  linkLabel?: string;
};

export function AnnouncementBar({
  message = "Rentrée 2025-2026. Consultez les annonces officielles de l'établissement.",
  href = "/dashboard/annonces",
  linkLabel = "Lire les annonces",
}: AnnouncementBarProps) {
  return (
    <div className="sgep-announcement">
      <span>{message}</span>
      {href && (
        <a href={href} className="ml-2 inline-flex items-center gap-1">
          {linkLabel}
          <svg viewBox="0 0 16 16" className="h-3.5 w-3.5" aria-hidden>
            <path
              d="M5 3l5 5-5 5"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </a>
      )}
    </div>
  );
}
