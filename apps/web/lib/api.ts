const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Source = {
  id: string;
  name: string;
  provider_type: string;
  status: string;
  config: Record<string, unknown>;
};

export type Claim = {
  id: string;
  text: string;
  status: string;
  staleness_risk: string;
  created_at: string;
};

export type PatchProposal = {
  id: string;
  original_text: string;
  proposed_text: string;
  citation_ids: string[];
  status: string;
  created_at: string;
};

export type AuditEvent = {
  id: string;
  action: string;
  aggregate_type: string;
  aggregate_id: string;
  created_at: string;
};

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function getSources() {
  return fetchJson<Source[]>("/sources");
}

export function getClaims() {
  return fetchJson<Claim[]>("/claims");
}

export function getPatchProposals() {
  return fetchJson<PatchProposal[]>("/patch-proposals");
}

export function getPatchProposal(id: string) {
  return fetchJson<PatchProposal>(`/patch-proposals/${id}`);
}

export function getAuditEvents() {
  return fetchJson<AuditEvent[]>("/audit");
}
