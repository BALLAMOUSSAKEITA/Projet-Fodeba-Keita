export function AuroraRibbon({ className = "" }: { className?: string }) {
  return (
    <div
      className={`pointer-events-none absolute inset-y-0 right-0 w-[min(55vw,640px)] overflow-hidden ${className}`}
      aria-hidden
    >
      <svg
        viewBox="0 0 640 800"
        preserveAspectRatio="xMaxYMid slice"
        className="h-full w-full opacity-80"
      >
        <defs>
          <linearGradient id="aurora" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#006aff" stopOpacity="0.85" />
            <stop offset="45%" stopColor="#a95af8" stopOpacity="0.75" />
            <stop offset="100%" stopColor="#fb9ce5" stopOpacity="0.55" />
          </linearGradient>
          <filter id="blur">
            <feGaussianBlur stdDeviation="18" />
          </filter>
        </defs>
        <path
          d="M120 120 C 220 40, 360 180, 420 80 S 620 220, 560 360 S 480 520, 640 620 L 640 800 L 80 800 C 140 640, 60 420, 120 120 Z"
          fill="url(#aurora)"
          filter="url(#blur)"
        />
        <path
          d="M200 200 C 280 140, 400 260, 460 180 S 580 300, 520 420 S 440 560, 600 660"
          fill="none"
          stroke="url(#aurora)"
          strokeWidth="48"
          strokeLinecap="round"
          opacity="0.35"
          filter="url(#blur)"
        />
      </svg>
    </div>
  );
}
