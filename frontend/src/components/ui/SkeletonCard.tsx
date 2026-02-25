export function SkeletonCard() {
  return (
    <div className="bg-white/30 rounded-2xl p-8 animate-pulse">
      <div className="h-10 w-10 bg-gray-300 rounded-full mb-4"></div>
      <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
      <div className="h-3 bg-gray-300 rounded w-1/2"></div>
    </div>
  );
}
