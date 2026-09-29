type LogoProps = {
  className?: string;
};

export function Logo({ className = "" }: LogoProps) {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="flex h-10 w-10 items-center justify-center rounded-[14px] border border-cloud bg-snow">
        <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden>
          <path
            d="M12 3 4 7v10l8 4 8-4V7l-8-4Z"
            fill="none"
            stroke="#09090b"
            strokeWidth="1.5"
            strokeLinejoin="round"
          />
          <path d="M12 7v10" stroke="#52525b" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </div>
      <div>
        <p className="text-[13px] font-semibold leading-none text-obsidian">SGEP</p>
        <p className="mt-1 text-[12px] text-steel">Fodeba Keita</p>
      </div>
    </div>
  );
}
