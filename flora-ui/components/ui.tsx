import Link from "next/link";
import type { ReactNode } from "react";
import type { StatusTone } from "@/lib/mock-data";

const badgeStyles: Record<StatusTone, string> = {
  neutral: "border-[#d8dedb] bg-[#f5f7f6] text-[#56615d]",
  good: "border-[#c9ded5] bg-[#e8f3ee] text-moss",
  warn: "border-[#ead8c5] bg-[#f7efe7] text-clay",
  bad: "border-[#edcbc6] bg-[#f7e8e8] text-[#9b3d32]",
  info: "border-[#c9d8ea] bg-[#e8eef7] text-[#365f91]",
};

export function PageHeader({ title, description, actions }: { title: string; description: string; actions?: ReactNode }) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-4">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-moss">Flora</p>
        <h1 className="mt-2 text-2xl font-semibold">{title}</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-[#56615d]">{description}</p>
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}

export function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`rounded border border-[#d9e3de] bg-white shadow-sm ${className}`}>{children}</div>;
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: StatusTone }) {
  return (
    <span className={`inline-flex rounded border px-2 py-1 text-xs font-medium capitalize ${badgeStyles[tone]}`}>
      {children}
    </span>
  );
}

export function MetricCard({ label, value, detail, href }: { label: string; value: string | number; detail: string; href: string }) {
  return (
    <Link href={href} className="rounded border border-[#d9e3de] bg-white p-4 shadow-sm hover:border-moss">
      <div className="text-sm text-[#56615d]">{label}</div>
      <div className="mt-2 text-3xl font-semibold">{value}</div>
      <div className="mt-2 text-xs text-[#6d7773]">{detail}</div>
    </Link>
  );
}

export function SectionTitle({ title, detail }: { title: string; detail?: string }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <h2 className="text-base font-semibold">{title}</h2>
      {detail && <span className="text-xs text-[#6d7773]">{detail}</span>}
    </div>
  );
}

export function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <Panel className="p-5">
      <div className="text-sm font-medium">{title}</div>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-[#56615d]">{description}</p>
    </Panel>
  );
}
