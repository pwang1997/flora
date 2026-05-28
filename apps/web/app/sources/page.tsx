import { getSources } from "@/lib/api";

export default async function SourcesPage() {
  const sources = await getSources().catch(() => []);
  return (
    <section>
      <h1 className="text-2xl font-semibold">Sources</h1>
      <div className="mt-5 overflow-hidden rounded border border-[#d9e3de] bg-white">
        {sources.map((source) => (
          <div key={source.id} className="grid grid-cols-[1fr_160px_120px] border-b border-[#edf2ef] p-4 last:border-0">
            <span className="font-medium">{source.name}</span>
            <span className="text-sm text-[#56615d]">{source.provider_type}</span>
            <span className="text-sm text-moss">{source.status}</span>
          </div>
        ))}
        {sources.length === 0 && <div className="p-4 text-sm text-[#56615d]">No sources configured.</div>}
      </div>
    </section>
  );
}
