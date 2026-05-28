import { getClaims } from "@/lib/api";

export default async function ClaimsPage() {
  const claims = await getClaims().catch(() => []);
  return (
    <section>
      <h1 className="text-2xl font-semibold">Claims</h1>
      <div className="mt-5 overflow-hidden rounded border border-[#d9e3de] bg-white">
        {claims.map((claim) => (
          <div key={claim.id} className="grid grid-cols-[1fr_120px_120px] gap-4 border-b border-[#edf2ef] p-4 last:border-0">
            <span>{claim.text}</span>
            <span className="text-sm text-clay">{claim.staleness_risk}</span>
            <span className="text-sm text-[#56615d]">{claim.status}</span>
          </div>
        ))}
        {claims.length === 0 && <div className="p-4 text-sm text-[#56615d]">No claims extracted yet.</div>}
      </div>
    </section>
  );
}
