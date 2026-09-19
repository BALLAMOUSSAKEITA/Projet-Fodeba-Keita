type LogoProps = {
  compact?: boolean;
  className?: string;
};

export function Logo({ compact = false, className = "" }: LogoProps) {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[6px] border border-hairline bg-marble">
        <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden>
          <path
            d="M12 3 4 7v10l8 4 8-4V7l-8-4Z"
            fill="none"
            stroke="#1b1b1b"
            strokeWidth="1.5"
            strokeLinejoin="round"
          />
          <path d="M12 7v10M8 9.5l4-2 4 2" stroke="#0d7f8c" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </div>
      {!compact && (
        <div>
          <p className="text-[13px] font-semibold leading-none tracking-wide text-graphite-ink">SGEP</p>
          <p className="mt-1 text-[12px] leading-tight text-steel">Fodeba Keita</p>
        </div>
      )}
    </div>
  );
}
