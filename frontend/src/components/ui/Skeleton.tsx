type SkeletonProps = {
  className?: string;
};

export function Skeleton({ className = "" }: SkeletonProps) {
  return <div className={`sgep-skeleton ${className}`} aria-hidden />;
}

export function KpiTileSkeleton() {
  return (
    <div className="sgep-kpi-tile">
      <Skeleton className="h-3.5 w-28" />
      <Skeleton className="mt-4 h-9 w-20" />
      <Skeleton className="mt-3 h-3 w-36" />
    </div>
  );
}
