import Link from "next/link";
import { getClaims, getPatchProposals, getSources } from "@/lib/api";

export default async function Home() {
  const [sources, claims, patches] = await Promise.allSettled([
    getSources(),
    getClaims(),
    getPatchProposals(),
  ]);
  const sourceCount = sources.status === "fulfilled" ? sources.value.length : 0;
  const claimCount = claims.status === "fulfilled" ? claims.value.length : 0;
  const patchCount = patches.status === "fulfilled" ? patches.value.length : 0;

  return (
    <section className="max-w-5xl">
      <h1 className="text-3xl font-semibold">Knowledge maintenance queue</h1>
      <div className="mt-6 grid grid-cols-3 gap-4">
        <Metric label="Sources" value={sourceCount} href="/sources" />
        <Metric label="Claims" value={claimCount} href="/claims" />
        <Metric label="Patch proposals" value={patchCount} href="/patches" />
      </div>
      <div className="mt-8 rounded border border-[#d9e3de] bg-white p-5">
        <h2 className="text-lg font-medium">Review loop</h2>
        <p className="mt-2 text-sm text-[#56615d]">
          Connect local Markdown, scan for time-sensitive claims, review generated proposals, and approve write-back.
        </p>
      </div>
    </section>
  );
}

function Metric({ label, value, href }: { label: string; value: number; href: string }) {
  return (
    <Link href={href} className="rounded border border-[#d9e3de] bg-white p-4 hover:border-moss">
      <div className="text-sm text-[#56615d]">{label}</div>
      <div className="mt-2 text-3xl font-semibold">{value}</div>
    </Link>
  );
}
