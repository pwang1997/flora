import Link from "next/link";
import { Badge, PageHeader, Panel, SectionTitle } from "@/components/ui";
import { patchProposals, statusTone } from "@/lib/mock-data";
import { formatDate, shortId } from "@/lib/format";

export default function PatchesPage() {
  return (
    <section className="max-w-6xl">
      <PageHeader
        title="Patch proposals"
        description="Mock review queue for citation-backed updates. Proposals require explicit approval before write-back."
      />

      <div className="mt-6">
        <SectionTitle title="Review queue" detail={`${patchProposals.length} proposals`} />
        <div className="mt-3 grid gap-3">
          {patchProposals.map((patch) => (
            <Link key={patch.id} href={`/patches/${patch.id}`}>
              <Panel className="p-4 hover:border-moss">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <div className="text-xs text-[#6d7773]">
                      {shortId(patch.id)} · {patch.document} · {formatDate(patch.createdAt)}
                    </div>
                    <p className="mt-2 line-clamp-2 text-sm leading-6">{patch.originalText}</p>
                  </div>
                  <Badge tone={statusTone(patch.status)}>{patch.status}</Badge>
                </div>
              </Panel>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
