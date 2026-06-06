"use client";

import { Badge, PageHeader, Panel, SectionTitle } from "@/components/ui";
import { createSource, deleteSource, getSources, type Source, type SourceCreate } from "@/lib/api";
import { formatDate } from "@/lib/format";
import { statusTone } from "@/lib/mock-data";
import { useEffect, useState } from "react";

const providerOptions: Array<{ label: string; value: SourceCreate["provider_type"] }> = [
  { label: "Obsidian vault", value: "obsidian" },
  { label: "Local Markdown", value: "local_markdown" },
  { label: "GitHub", value: "github" },
  { label: "Notion", value: "notion" },
];

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [name, setName] = useState("My Obsidian Vault");
  const [providerType, setProviderType] = useState<SourceCreate["provider_type"]>("obsidian");
  const [configJson, setConfigJson] = useState('{\n  "source_path": "/Users/pwang/Documents/Knowledge"\n}');
  const [listLoading, setListLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function loadSources() {
      try {
        const loadedSources = await getSources();
        if (active) setSources(loadedSources);
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : "Failed to load sources");
      } finally {
        if (active) setListLoading(false);
      }
    }

    loadSources();

    return () => {
      active = false;
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const config = JSON.parse(configJson);

      const newSource = await createSource({
        name,
        provider_type: providerType,
        config,
      });
      setSources((currentSources) => [...currentSources, newSource]);
      setName("");
      setProviderType("obsidian");
      setConfigJson('{\n  "source_path": ""\n}');
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create source");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="max-w-6xl">
      <PageHeader
        title="Sources"
        description="Create and manage data sources for Flora. Connect local Markdown folders and Obsidian vaults."
      />

      <div className="mt-6 grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
        <Panel className="p-5">
          <SectionTitle title="Create source" />
          <form onSubmit={handleSubmit} className="mt-4 grid gap-4">
            <label className="grid gap-2 text-sm font-medium">
              Source name
              <input
                className="rounded border border-[#cfdad4] px-3 py-2 font-normal outline-none focus:border-moss"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                minLength={1}
              />
            </label>
            <label className="grid gap-2 text-sm font-medium">
              Provider
              <select
                className="rounded border border-[#cfdad4] px-3 py-2 font-normal outline-none focus:border-moss"
                value={providerType}
                onChange={(e) => setProviderType(e.target.value as SourceCreate["provider_type"])}
              >
                {providerOptions.map((provider) => (
                  <option key={provider.value} value={provider.value}>
                    {provider.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="grid gap-2 text-sm font-medium">
              Source config JSON
              <textarea
                className="min-h-32 resize-y rounded border border-[#cfdad4] px-3 py-2 font-mono text-sm font-normal outline-none focus:border-moss"
                value={configJson}
                onChange={(e) => setConfigJson(e.target.value)}
                spellCheck={false}
              />
            </label>
            {error && <div className="rounded bg-red-100 p-3 text-sm text-red-700">{error}</div>}
            <button
              className="rounded bg-moss px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
              type="submit"
              disabled={loading}
            >
              {loading ? "Creating..." : "Create source"}
            </button>
          </form>
        </Panel>

        <Panel className="overflow-hidden">
          <div className="border-b border-[#edf2ef] p-4">
            <SectionTitle title="Connected sources" detail={`${sources.length} total`} />
          </div>
          {listLoading ? (
            <div className="p-4 text-sm text-[#6d7773]">Loading sources...</div>
          ) : sources.length === 0 ? (
            <div className="p-4 text-sm text-[#6d7773]">No sources connected yet</div>
          ) : (
            sources.map((source) => (
              <div key={source.id} className="grid grid-cols-[1fr_120px_110px] items-center gap-4 border-b border-[#edf2ef] p-4 last:border-0">
                <div className="min-w-0">
                  <div className="font-medium">{source.name}</div>
                  <div className="mt-1 truncate text-xs text-[#6d7773]">{source.id}</div>
                  <div className="mt-2 text-xs text-[#6d7773]">
                    {source.document_count} docs · {source.changed_count} changed · last scan{" "}
                    {source.last_scan_at ? formatDate(source.last_scan_at) : "never"}
                  </div>
                </div>
                <span className="text-sm text-[#56615d]">{source.provider_type}</span>
                <div className="flex justify-end">
                  <Badge tone={statusTone(source.status)}>{source.status}</Badge>
                  <button
                    className="rounded bg-red-100 px-3 py-1 text-sm font-medium text-red-700 hover:bg-red-200"
                    onClick={() => deleteSource(source.id)}
                  >
                    Delete
                  </button>
                </div>

              </div>
            ))
          )}
        </Panel>
      </div>
    </section>
  );
}
