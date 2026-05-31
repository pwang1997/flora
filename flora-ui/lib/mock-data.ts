export type StatusTone = "neutral" | "good" | "warn" | "bad" | "info";

export const sources = [
  {
    id: "src-obsidian",
    name: "Personal Obsidian Vault",
    provider: "Obsidian",
    path: "/Users/pwang/Documents/Knowledge",
    status: "active",
    lastScan: "2026-05-30T13:20:00-04:00",
    documents: 184,
    changed: 12,
  },
  {
    id: "src-md-research",
    name: "Research Markdown",
    provider: "Local Markdown",
    path: "/Users/pwang/Desktop/research-notes",
    status: "active",
    lastScan: "2026-05-30T10:05:00-04:00",
    documents: 52,
    changed: 3,
  },
];

export const scans = [
  {
    id: "scan-1042",
    source: "Personal Obsidian Vault",
    status: "running",
    phase: "Claim extraction",
    documentsSeen: 184,
    documentsChanged: 12,
    claimsExtracted: 31,
    startedAt: "2026-05-30T13:20:00-04:00",
  },
  {
    id: "scan-1041",
    source: "Research Markdown",
    status: "completed",
    phase: "Audit recorded",
    documentsSeen: 52,
    documentsChanged: 3,
    claimsExtracted: 8,
    startedAt: "2026-05-30T10:05:00-04:00",
  },
];

export const workerEvents = [
  {
    id: "evt-8001",
    eventType: "SOURCE_SCAN_REQUESTED",
    status: "processing",
    worker: "flora-worker-1",
    attempts: 1,
    availableAt: "now",
    detail: "Listing Markdown files from Personal Obsidian Vault",
  },
  {
    id: "evt-8000",
    eventType: "CLAIM_VERIFICATION_REQUESTED",
    status: "pending",
    worker: "-",
    attempts: 0,
    availableAt: "in 2 min",
    detail: "Waiting for evidence lookup slot",
  },
  {
    id: "evt-7999",
    eventType: "PATCH_GENERATION_REQUESTED",
    status: "processed",
    worker: "flora-worker-1",
    attempts: 1,
    availableAt: "processed",
    detail: "Generated proposal pp-314",
  },
  {
    id: "evt-7998",
    eventType: "PATCH_APPLICATION_REQUESTED",
    status: "failed",
    worker: "flora-worker-2",
    attempts: 3,
    availableAt: "paused",
    detail: "Original text changed before write-back",
  },
];

export const claims = [
  {
    id: "claim-771",
    source: "Personal Obsidian Vault",
    document: "Investing/ETF Landscape.md",
    text: "As of 2024, Qdrant is the latest vector database option considered for Flora local development.",
    risk: "high",
    status: "verification requested",
    age: "12 min",
  },
  {
    id: "claim-770",
    source: "Research Markdown",
    document: "AI Agents/MCP Notes.md",
    text: "Current MCP server transports are mostly HTTP streamable transports for production deployments.",
    risk: "medium",
    status: "evidence collected",
    age: "1 hr",
  },
  {
    id: "claim-769",
    source: "Personal Obsidian Vault",
    document: "Taxes/TFSA.md",
    text: "The 2025 TFSA contribution limit is 7000 CAD.",
    risk: "high",
    status: "patch proposed",
    age: "3 hr",
  },
];

export const patchProposals = [
  {
    id: "pp-314",
    claimId: "claim-769",
    source: "Personal Obsidian Vault",
    document: "Taxes/TFSA.md",
    status: "pending",
    originalText: "The 2025 TFSA contribution limit is 7000 CAD.",
    proposedText: "The 2025 TFSA contribution limit should be verified against the latest CRA guidance before use.",
    citations: ["CRA contribution room page", "Archived Flora evidence snapshot"],
    createdAt: "2026-05-30T12:50:00-04:00",
  },
  {
    id: "pp-313",
    claimId: "claim-770",
    source: "Research Markdown",
    document: "AI Agents/MCP Notes.md",
    status: "approved",
    originalText: "Current MCP server transports are mostly HTTP streamable transports for production deployments.",
    proposedText: "Production MCP deployments commonly use HTTP streamable transports, while local development may still use stdio.",
    citations: ["MCP transport spec", "Flora evidence stub"],
    createdAt: "2026-05-30T10:35:00-04:00",
  },
];

export const auditEvents = [
  {
    id: "audit-920",
    action: "SOURCE_SCAN_REQUESTED",
    aggregate: "source",
    target: "Personal Obsidian Vault",
    createdAt: "2026-05-30T13:20:00-04:00",
  },
  {
    id: "audit-919",
    action: "CLAIMS_EXTRACTED",
    aggregate: "document_snapshot",
    target: "ETF Landscape.md",
    createdAt: "2026-05-30T13:23:00-04:00",
  },
  {
    id: "audit-918",
    action: "PATCH_PROPOSED",
    aggregate: "patch_proposal",
    target: "pp-314",
    createdAt: "2026-05-30T12:50:00-04:00",
  },
  {
    id: "audit-917",
    action: "PATCH_APPROVED",
    aggregate: "patch_proposal",
    target: "pp-313",
    createdAt: "2026-05-30T10:42:00-04:00",
  },
];

export function statusTone(status: string): StatusTone {
  const normalized = status.toLowerCase();
  if (["active", "completed", "processed", "approved", "applied"].includes(normalized)) return "good";
  if (["pending", "running", "processing", "verification requested"].includes(normalized)) return "info";
  if (["high", "failed"].includes(normalized)) return "bad";
  if (["medium", "patch proposed", "evidence collected"].includes(normalized)) return "warn";
  return "neutral";
}
