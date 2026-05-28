import { getPatchProposal } from "@/lib/api";

export default async function PatchDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const patch = await getPatchProposal(id);
  return (
    <section className="max-w-5xl">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold">Patch review</h1>
        <span className="rounded bg-mist px-3 py-1 text-sm text-moss">{patch.status}</span>
      </div>
      <div className="mt-5 grid grid-cols-2 gap-4">
        <div className="rounded border border-[#d9e3de] bg-white p-4">
          <h2 className="text-sm font-medium text-[#56615d]">Original</h2>
          <p className="mt-3 whitespace-pre-wrap text-sm">{patch.original_text}</p>
        </div>
        <div className="rounded border border-[#d9e3de] bg-white p-4">
          <h2 className="text-sm font-medium text-[#56615d]">Proposed</h2>
          <p className="mt-3 whitespace-pre-wrap text-sm">{patch.proposed_text}</p>
        </div>
      </div>
      <div className="mt-4 rounded border border-[#d9e3de] bg-white p-4">
        <h2 className="text-sm font-medium text-[#56615d]">Citations</h2>
        <div className="mt-3 flex flex-wrap gap-2">
          {patch.citation_ids.map((citation) => (
            <span key={citation} className="rounded bg-[#f1f4f2] px-2 py-1 text-xs">
              {citation}
            </span>
          ))}
          {patch.citation_ids.length === 0 && <span className="text-sm text-[#56615d]">No citations linked.</span>}
        </div>
      </div>
    </section>
  );
}
