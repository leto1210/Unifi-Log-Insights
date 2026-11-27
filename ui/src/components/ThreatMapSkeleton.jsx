export default function ThreatMapSkeleton() {
  return (
    <div className="h-full flex flex-col animate-pulse">
      <div className="flex items-center gap-2 px-4 py-2 border-b border-gray-800">
        <div className="h-7 w-10 bg-gray-800 rounded" />
        <div className="h-7 w-10 bg-gray-800 rounded" />
        <div className="h-7 w-10 bg-gray-800 rounded" />
      </div>
      <div className="flex-1 bg-black" />
    </div>
  )
}
