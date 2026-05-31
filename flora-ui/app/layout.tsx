import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Flora",
  description: "Maintenance layer for living knowledge bases",
};

const nav = [
  ["Overview", "/"],
  ["Sources", "/sources"],
  ["Scans", "/scans"],
  ["Workers", "/workers"],
  ["Claims", "/claims"],
  ["Patches", "/patches"],
  ["Audit", "/audit"],
  ["Settings", "/settings"],
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#f7faf8] text-ink">
        <div className="grid min-h-screen grid-cols-[230px_1fr]">
          <aside className="border-r border-[#d9e3de] bg-white px-5 py-6">
            <Link href="/" className="block">
              <span className="block text-xl font-semibold text-moss">Flora</span>
              <span className="mt-1 block text-xs text-[#6d7773]">Knowledge maintenance</span>
            </Link>
            <nav className="mt-8 flex flex-col gap-1">
              {nav.map(([label, href]) => (
                <Link key={href} href={href} className="rounded px-3 py-2 text-sm hover:bg-mist">
                  {label}
                </Link>
              ))}
            </nav>
            <div className="mt-8 rounded border border-[#d9e3de] bg-[#f7faf8] p-3 text-xs leading-5 text-[#56615d]">
              Mock UI mode. Data shown here mirrors the intended MVP workflow and is not connected to `flora-core` yet.
            </div>
          </aside>
          <main className="px-8 py-7">{children}</main>
        </div>
      </body>
    </html>
  );
}
