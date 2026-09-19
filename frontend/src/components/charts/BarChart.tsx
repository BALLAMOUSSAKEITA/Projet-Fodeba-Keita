type Props = {
  labels: string[];
  values: number[];
  color?: string;
  formatValue?: (n: number) => string;
};

export function BarChart({ labels, values, color = "bg-emerald-600", formatValue }: Props) {
  const max = Math.max(...values, 1);

  if (labels.length === 0) {
    return <p className="text-sm text-slate-500">Aucune donnée.</p>;
  }

  return (
    <div className="space-y-3">
      {labels.map((label, i) => {
        const v = values[i] ?? 0;
        const pct = Math.round((v / max) * 100);
        return (
          <div key={label}>
            <div className="mb-1 flex justify-between text-xs text-slate-600">
              <span>{label}</span>
              <span className="font-medium">{formatValue ? formatValue(v) : v}</span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-slate-100">
              <div
                className={`h-full rounded-full ${color} transition-all`}
                style={{ width: `${Math.max(pct, 2)}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
