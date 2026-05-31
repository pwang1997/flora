import { Badge, PageHeader, Panel, SectionTitle } from "@/components/ui";
import { claims, statusTone } from "@/lib/mock-data";
import { shortId } from "@/lib/format";

export default function ClaimsPage() {
  return (
    <section className="max-w-6xl">
      <PageHeader
        title="Claims"
        description="Mock claim inbox showing factual statements extracted from note snapshots and classified by staleness risk."
      />

      <Panel className="mt-6 overflow-hidden">
        <div className="border-b border-[#edf2ef] p-4">
          <SectionTitle title="Claim inbox" detail={`${claims.length} claims`} />
        </div>
        {claims.map((claim) => (
          <div key={claim.id} className="grid grid-cols-[1fr_110px_150px_80px] gap-4 border-b border-[#edf2ef] p-4 text-sm last:border-0">
            <div className="min-w-0">
              <div className="text-xs text-[#6d7773]">
                {shortId(claim.id)} · {claim.document}
              </div>
              <p className="mt-2 leading-6">{claim.text}</p>
              <div className="mt-2 text-xs text-[#6d7773]">{claim.source}</div>
            </div>
            <Badge tone={statusTone(claim.risk)}>{claim.risk}</Badge>
            <Badge tone={statusTone(claim.status)}>{claim.status}</Badge>
            <span className="text-xs text-[#6d7773]">{claim.age}</span>
          </div>
        ))}
      </Panel>
    </section>
  );
}
