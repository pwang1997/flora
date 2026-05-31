import { Badge, PageHeader, Panel, SectionTitle } from "@/components/ui";
import { statusTone, workerEvents } from "@/lib/mock-data";
import { shortId } from "@/lib/format";

export default function WorkersPage() {
  return (
    <section className="max-w-6xl">
      <PageHeader
        title="Worker states"
        description="Mock PostgreSQL outbox view showing pending, processing, processed, and failed worker events."
      />

      <Panel className="mt-6 overflow-hidden">
        <div className="border-b border-[#edf2ef] p-4">
          <SectionTitle title="Outbox queue" detail={`${workerEvents.length} events`} />
        </div>
        {workerEvents.map((event) => (
          <div key={event.id} className="grid grid-cols-[100px_1fr_120px_90px_110px] gap-4 border-b border-[#edf2ef] p-4 text-sm last:border-0">
            <span className="text-xs text-[#6d7773]">{shortId(event.id)}</span>
            <div>
              <div className="font-medium">{event.eventType}</div>
              <div className="mt-1 text-xs text-[#6d7773]">{event.detail}</div>
            </div>
            <span className="text-[#56615d]">{event.worker}</span>
            <span className="text-[#56615d]">{event.attempts} tries</span>
            <Badge tone={statusTone(event.status)}>{event.status}</Badge>
          </div>
        ))}
      </Panel>
    </section>
  );
}
