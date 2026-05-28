import { getAuditEvents } from "@/lib/api";

export default async function AuditPage() {
  const events = await getAuditEvents().catch(() => []);
  return (
    <section>
      <h1 className="text-2xl font-semibold">Audit</h1>
      <div className="mt-5 overflow-hidden rounded border border-[#d9e3de] bg-white">
        {events.map((event) => (
          <div key={event.id} className="grid grid-cols-[220px_160px_1fr] gap-4 border-b border-[#edf2ef] p-4 text-sm last:border-0">
            <span className="font-medium">{event.action}</span>
            <span className="text-[#56615d]">{event.aggregate_type}</span>
            <span className="text-[#56615d]">{new Date(event.created_at).toLocaleString()}</span>
          </div>
        ))}
        {events.length === 0 && <div className="p-4 text-sm text-[#56615d]">No audit events.</div>}
      </div>
    </section>
  );
}
