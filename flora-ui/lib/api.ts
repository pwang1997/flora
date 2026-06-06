const API_URL = process.env.NEXT_PUBLIC_FLORA_CORE_URL ?? "http://localhost:8000";

export type HealthResponse = {
  status: string;
};

export interface Source {
  id: string;
  name: string;
  provider_type: "local_markdown" | "obsidian";
  config: Record<string, unknown>;
  status: string;
  document_count: number;
  changed_count: number;
  last_scan_at: string | null;
}

export interface SourceCreate {
  name: string;
  provider_type: Source["provider_type"];
  config: Record<string, unknown>;
}

type ApiErrorDetail = string | { msg?: string } | Array<{ msg?: string }>;

function formatApiError(status: number, detail: ApiErrorDetail | undefined): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const messages = detail.map((item) => item.msg).filter(Boolean);
    if (messages.length > 0) return messages.join(", ");
  }
  if (detail && typeof detail === "object" && "msg" in detail && detail.msg) return detail.msg;
  return `API request failed: ${status}`;
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    cache: "no-store",
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!response.ok) {
    let detail: ApiErrorDetail | undefined;
    try {
      detail = (await response.json()).detail;
    } catch {
      detail = undefined;
    }
    throw new Error(formatApiError(response.status, detail));
  }
  return response.json() as Promise<T>;
}

export function getHealth() {
  return fetchJson<HealthResponse>("/health");
}

export function getSources() {
  return fetchJson<Source[]>("/v1/sources");
}

export function createSource(payload: SourceCreate) {
  return fetchJson<Source>("/v1/sources", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
