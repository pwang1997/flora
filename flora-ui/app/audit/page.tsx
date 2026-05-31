import { PageHeader, Panel, SectionTitle } from "@/components/ui";
import { auditEvents } from "@/lib/mock-data";
import { formatDate, shortId } from "@/lib/format";

export default function AuditPage() {
  return (
    <section className="max-w-6xl">
      <PageHeader
        title="Audit"
        description="Mock audit timeline for scan requests, claim extraction, evidence collection, proposal creation, and approval decisions."
      />

      <Panel className="mt-6 overflow-hidden">
        <div className="border-b border-[#edf2ef] p-4">
          <SectionTitle title="Recent events" detail={`${auditEvents.length} events`} />
        </div>
        {auditEvents.map((event) => (
          <div key={event.id} className="grid grid-cols-[150px_220px_1fr_150px] gap-4 border-b border-[#edf2ef] p-4 text-sm last:border-0">
            <span className="text-xs text-[#6d7773]">{shortId(event.id)}</span>
            <span className="font-medium">{event.action}</span>
            <span className="text-[#56615d]">
              {event.aggregate} · {event.target}
            </span>
            <span className="text-xs text-[#6d7773]">{formatDate(event.createdAt)}</span>
          </div>
        ))}
      </Panel>
    </section>
  );
}
