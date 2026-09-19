export function LoginPreview() {
  const bars = [42, 68, 55, 82, 61, 74, 48];

  return (
    <div className="sgep-card-elevated hidden overflow-hidden lg:block">
      <div className="flex gap-0 border-b border-hairline">
        <div className="w-[140px] shrink-0 border-r border-hairline bg-drafting-gray/60 p-4">
          <div className="mb-4 h-2 w-16 rounded bg-hairline" />
          {["Vue", "Élèves", "Notes", "Finance", "Rapports"].map((item, i) => (
            <div
              key={item}
              className={`mb-2 rounded-[6px] px-2 py-1.5 text-[11px] ${
                i === 0
                  ? "bg-marble font-medium text-graphite-ink shadow-sm"
                  : "text-steel"
              }`}
            >
              {item}
            </div>
          ))}
        </div>
        <div className="min-w-0 flex-1 p-5">
          <p className="text-[13px] font-medium text-graphite-ink">Indicateurs du mois</p>
          <p className="mt-0.5 text-[11px] text-steel">Maternelle et primaire</p>
          <div className="mt-5 grid grid-cols-2 gap-3">
            {[
              { label: "Élèves", value: "842" },
              { label: "Classes", value: "28" },
              { label: "Recettes", value: "12,4 M" },
              { label: "Présence", value: "94 %" },
            ].map((kpi) => (
              <div
                key={kpi.label}
                className="rounded-[12px] border border-hairline bg-marble px-3 py-2.5"
              >
                <p className="text-[10px] text-steel">{kpi.label}</p>
                <p className="mt-1 text-[18px] font-semibold tracking-tight text-graphite-ink">
                  {kpi.value}
                </p>
              </div>
            ))}
          </div>
          <div className="mt-5 rounded-[12px] border border-hairline bg-marble p-3">
            <p className="mb-3 text-[10px] text-steel">Encaissements hebdomadaires</p>
            <div className="flex h-20 items-end gap-1.5">
              {bars.map((h, i) => (
                <div
                  key={i}
                  className="flex-1 rounded-t-[3px] bg-mint-signal/80"
                  style={{ height: `${h}%` }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
