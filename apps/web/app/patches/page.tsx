import Link from "next/link";
import { getPatchProposals } from "@/lib/api";

export default async function PatchesPage() {
  const patches = await getPatchProposals().catch(() => []);
  return (
    <section>
      <h1 className="text-2xl font-semibold">Patch proposals</h1>
      <div className="mt-5 grid gap-3">
        {patches.map((patch) => (
          <Link key={patch.id} href={`/patches/${patch.id}`} className="rounded border border-[#d9e3de] bg-white p-4 hover:border-moss">
            <div className="flex items-center justify-between gap-4">
              <p className="line-clamp-2 text-sm">{patch.original_text}</p>
              <span className="rounded bg-mist px-2 py-1 text-xs text-moss">{patch.status}</span>
            </div>
          </Link>
        ))}
        {patches.length === 0 && <div className="rounded border border-[#d9e3de] bg-white p-4 text-sm text-[#56615d]">No patch proposals.</div>}
      </div>
    </section>
  );
}
