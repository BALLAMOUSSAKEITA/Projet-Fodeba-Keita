"use client";

type AnnouncementBarProps = {
  message?: string;
  href?: string;
  linkLabel?: string;
};

export function AnnouncementBar({
  message = "Année scolaire 2025–2026 — Inscriptions et bulletins disponibles dans SGEP.",
  href = "/dashboard/annonces",
  linkLabel = "Voir les annonces →",
}: AnnouncementBarProps) {
  return (
    <div className="sgep-announcement">
      <span>{message} </span>
      {href && (
        <a href={href}>{linkLabel}</a>
      )}
    </div>
  );
}
