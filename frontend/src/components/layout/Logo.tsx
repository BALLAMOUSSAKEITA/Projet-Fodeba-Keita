type LogoProps = {
  className?: string;
};

export function Logo({ className = "" }: LogoProps) {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="flex h-9 w-9 items-center justify-center rounded-md border border-silver-mist/30 bg-midnight-navy">
        <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden>
          <path
            d="M12 3 4 7v10l8 4 8-4V7l-8-4Z"
            fill="none"
            stroke="#34e8bb"
            strokeWidth="1.5"
            strokeLinejoin="round"
          />
          <path d="M12 7v10" stroke="#ffffff" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </div>
      <div>
        <p className="font-mono text-[11px] font-medium uppercase tracking-[0.08em] text-bioluminescent-teal">
          SGEP
        </p>
        <p className="text-[13px] font-medium leading-tight text-canvas-white">Fodeba Keita</p>
      </div>
    </div>
  );
}
