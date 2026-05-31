import { Badge, MetricCard, PageHeader, Panel, SectionTitle } from "@/components/ui";
import { auditEvents, claims, patchProposals, scans, sources, statusTone, workerEvents } from "@/lib/mock-data";
import { formatDate } from "@/lib/format";

export default function Home() {
  const runningScan = scans.find((scan) => scan.status === "running");
  const pendingPatches = patchProposals.filter((patch) => patch.status === "pending").length;
  const highRiskClaims = claims.filter((claim) => claim.risk === "high").length;
  const activeWorkers = workerEvents.filter((event) => event.status === "processing").length;

  return (
    <section className="max-w-6xl">
      <PageHeader
        title="Knowledge maintenance queue"
        description="Mock dashboard for the first Flora workflow: connect sources, scan notes, inspect worker activity, review claims, and approve citation-backed patch proposals."
      />

      <div className="mt-6 grid gap-4 md:grid-cols-4">
        <MetricCard label="Sources" value={sources.length} detail="Obsidian + Markdown" href="/sources" />
        <MetricCard label="High-risk claims" value={highRiskClaims} detail="Need verification" href="/claims" />
        <MetricCard label="Pending patches" value={pendingPatches} detail="Awaiting review" href="/patches" />
        <MetricCard label="Worker events" value={workerEvents.length} detail={`${activeWorkers} processing`} href="/workers" />
      </div>

      <div className="mt-8 grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
        <Panel className="p-5">
          <SectionTitle title="Active scan" detail={runningScan ? runningScan.id : "none"} />
          {runningScan ? (
            <div className="mt-5">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className="font-medium">{runningScan.source}</div>
                  <div className="mt-1 text-sm text-[#56615d]">{runningScan.phase}</div>
                </div>
                <Badge tone={statusTone(runningScan.status)}>{runningScan.status}</Badge>
              </div>
              <div className="mt-5 grid gap-3 md:grid-cols-3">
                <Stat label="Documents" value={runningScan.documentsSeen} />
                <Stat label="Changed" value={runningScan.documentsChanged} />
                <Stat label="Claims" value={runningScan.claimsExtracted} />
              </div>
            </div>
          ) : (
            <p className="mt-4 text-sm text-[#56615d]">No scan is currently running.</p>
          )}
        </Panel>

        <Panel className="p-5">
          <SectionTitle title="Recent audit" detail={`${auditEvents.length} events`} />
          <div className="mt-4 grid gap-3">
            {auditEvents.slice(0, 4).map((event) => (
              <div key={event.id} className="border-b border-[#edf2ef] pb-3 last:border-0 last:pb-0">
                <div className="text-sm font-medium">{event.action}</div>
                <div className="mt-1 text-xs text-[#6d7773]">
                  {event.target} · {formatDate(event.createdAt)}
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded border border-[#edf2ef] bg-[#f9fbfa] p-3">
      <div className="text-xs text-[#6d7773]">{label}</div>
      <div className="mt-1 text-xl font-semibold">{value}</div>
    </div>
  );
}
