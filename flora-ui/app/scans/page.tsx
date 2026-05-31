import { Badge, PageHeader, Panel } from "@/components/ui";
import { scans, statusTone } from "@/lib/mock-data";
import { formatDate, shortId } from "@/lib/format";

export default function ScansPage() {
  return (
    <section className="max-w-6xl">
      <PageHeader
        title="Scans"
        description="Mock scan monitor showing source traversal, changed documents, extracted claims, and current phase."
      />

      <div className="mt-6 grid gap-4">
        {scans.map((scan) => (
          <Panel key={scan.id} className="p-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="text-xs text-[#6d7773]">{shortId(scan.id)}</div>
                <h2 className="mt-1 text-base font-semibold">{scan.source}</h2>
                <p className="mt-1 text-sm text-[#56615d]">{scan.phase}</p>
              </div>
              <Badge tone={statusTone(scan.status)}>{scan.status}</Badge>
            </div>
            <div className="mt-5 grid gap-3 md:grid-cols-4">
              <ScanStat label="Started" value={formatDate(scan.startedAt)} />
              <ScanStat label="Documents seen" value={scan.documentsSeen} />
              <ScanStat label="Changed" value={scan.documentsChanged} />
              <ScanStat label="Claims extracted" value={scan.claimsExtracted} />
            </div>
          </Panel>
        ))}
      </div>
    </section>
  );
}

function ScanStat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded border border-[#edf2ef] bg-[#f9fbfa] p-3">
      <div className="text-xs text-[#6d7773]">{label}</div>
      <div className="mt-1 text-sm font-medium">{value}</div>
    </div>
  );
}
