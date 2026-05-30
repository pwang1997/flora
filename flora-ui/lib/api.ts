const API_URL = process.env.NEXT_PUBLIC_FLORA_CORE_URL ?? "http://localhost:8000";

export type HealthResponse = {
  status: string;
};

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function getHealth() {
  return fetchJson<HealthResponse>("/health");
}
