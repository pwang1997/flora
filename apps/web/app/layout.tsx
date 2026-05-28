import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Flora",
  description: "Maintenance layer for living knowledge bases",
};

const nav = [
  ["Sources", "/sources"],
  ["Scans", "/scans"],
  ["Claims", "/claims"],
  ["Patches", "/patches"],
  ["Audit", "/audit"],
  ["Settings", "/settings"],
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#f7faf8] text-ink">
        <div className="grid min-h-screen grid-cols-[220px_1fr]">
          <aside className="border-r border-[#d9e3de] bg-white px-5 py-6">
            <Link href="/" className="block text-xl font-semibold text-moss">
              Flora
            </Link>
            <nav className="mt-8 flex flex-col gap-1">
              {nav.map(([label, href]) => (
                <Link key={href} href={href} className="rounded px-3 py-2 text-sm hover:bg-mist">
                  {label}
                </Link>
              ))}
            </nav>
          </aside>
          <main className="px-8 py-7">{children}</main>
        </div>
      </body>
    </html>
  );
}
