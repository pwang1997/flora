import Link from "next/link";
import { Badge, PageHeader, Panel, SectionTitle } from "@/components/ui";
import { patchProposals, statusTone } from "@/lib/mock-data";
import { formatDate, shortId } from "@/lib/format";

export default async function PatchDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const patch = patchProposals.find((item) => item.id === id) ?? patchProposals[0];

  return (
    <section className="max-w-6xl">
      <PageHeader
        title="Patch review"
        description={`${shortId(patch.id)} for ${patch.document}, created ${formatDate(patch.createdAt)}.`}
        actions={<Badge tone={statusTone(patch.status)}>{patch.status}</Badge>}
      />

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Panel className="p-5">
          <SectionTitle title="Original claim" />
          <p className="mt-4 whitespace-pre-wrap text-sm leading-6">{patch.originalText}</p>
        </Panel>
        <Panel className="p-5">
          <SectionTitle title="Proposed patch" />
          <p className="mt-4 whitespace-pre-wrap text-sm leading-6">{patch.proposedText}</p>
        </Panel>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_320px]">
        <Panel className="p-5">
          <SectionTitle title="Citations" detail={`${patch.citations.length} linked`} />
          <div className="mt-4 flex flex-wrap gap-2">
            {patch.citations.map((citation) => (
              <span key={citation} className="rounded border border-[#d9e3de] bg-[#f9fbfa] px-3 py-2 text-sm">
                {citation}
              </span>
            ))}
          </div>
        </Panel>
        <Panel className="p-5">
          <SectionTitle title="Review actions" detail="mock controls" />
          <div className="mt-4 grid gap-3">
            <button className="rounded bg-moss px-4 py-2 text-sm font-medium text-white" type="button">
              Approve patch
            </button>
            <button className="rounded border border-[#c8d5ce] px-4 py-2 text-sm font-medium text-[#56615d]" type="button">
              Reject patch
            </button>
            <Link className="text-center text-sm text-moss" href="/patches">
              Back to queue
            </Link>
          </div>
        </Panel>
      </div>
    </section>
  );
}
