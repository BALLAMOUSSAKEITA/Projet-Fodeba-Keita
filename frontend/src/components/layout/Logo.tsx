type LogoProps = {
  className?: string;
  size?: "sm" | "md" | "lg";
};

export function Logo({ className = "", size = "md" }: LogoProps) {
  const iconSize = size === "sm" ? "h-9 w-9" : size === "lg" ? "h-12 w-12" : "h-10 w-10";
  const titleSize = size === "lg" ? "text-[16px]" : "text-[14px]";
  const subSize = size === "lg" ? "text-[13px]" : "text-[12px]";

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className={`${iconSize} flex items-center justify-center rounded-lg bg-teal-600`}>
        <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden>
          <path
            d="M12 3 4 7v10l8 4 8-4V7l-8-4Z"
            fill="none"
            stroke="#ffffff"
            strokeWidth="1.5"
            strokeLinejoin="round"
          />
          <path d="M12 7v10" stroke="rgba(255,255,255,0.6)" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </div>
      <div>
        <p className={`${titleSize} font-bold leading-none text-white`}>GSP</p>
        <p className={`mt-1 ${subSize} text-slate-400`}>Groupe scolaire privé · Fodeba Keita</p>
      </div>
    </div>
  );
}

export function LogoLight({ className = "" }: { className?: string }) {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-600">
        <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden>
          <path
            d="M12 3 4 7v10l8 4 8-4V7l-8-4Z"
            fill="none"
            stroke="#ffffff"
            strokeWidth="1.5"
            strokeLinejoin="round"
          />
          <path d="M12 7v10" stroke="rgba(255,255,255,0.6)" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </div>
      <div>
        <p className="text-[14px] font-bold leading-none text-slate-900">GSP</p>
        <p className="mt-1 text-[12px] text-slate-500">Groupe scolaire privé · Fodeba Keita</p>
      </div>
    </div>
  );
}
