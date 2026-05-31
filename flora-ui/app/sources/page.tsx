import { Badge, PageHeader, Panel, SectionTitle } from "@/components/ui";
import { sources, statusTone } from "@/lib/mock-data";
import { formatDate } from "@/lib/format";

export default function SourcesPage() {
  return (
    <section className="max-w-6xl">
      <PageHeader
        title="Sources"
        description="Mock source registry for local Markdown folders and Obsidian vaults. The form illustrates the source config shape Flora will send to the core service."
      />

      <div className="mt-6 grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
        <Panel className="p-5">
          <SectionTitle title="Create source" detail="mock form" />
          <div className="mt-4 grid gap-4">
            <label className="grid gap-2 text-sm font-medium">
              Source name
              <input className="rounded border border-[#cfdad4] px-3 py-2 font-normal outline-none focus:border-moss" defaultValue="My Obsidian Vault" />
            </label>
            <label className="grid gap-2 text-sm font-medium">
              Provider
              <select className="rounded border border-[#cfdad4] px-3 py-2 font-normal outline-none focus:border-moss" defaultValue="obsidian">
                <option value="obsidian">Obsidian vault</option>
                <option value="local_markdown">Local Markdown</option>
              </select>
            </label>
            <label className="grid gap-2 text-sm font-medium">
              Source config JSON
              <textarea
                className="min-h-32 resize-y rounded border border-[#cfdad4] px-3 py-2 font-mono text-sm font-normal outline-none focus:border-moss"
                defaultValue={'{\n  "root_path": "/Users/pwang/Documents/Knowledge"\n}'}
                spellCheck={false}
              />
            </label>
            <button className="rounded bg-moss px-4 py-2 text-sm font-medium text-white" type="button">
              Create source
            </button>
          </div>
        </Panel>

        <Panel className="overflow-hidden">
          <div className="border-b border-[#edf2ef] p-4">
            <SectionTitle title="Connected sources" detail={`${sources.length} total`} />
          </div>
          {sources.map((source) => (
            <div key={source.id} className="grid grid-cols-[1fr_120px_110px] items-center gap-4 border-b border-[#edf2ef] p-4 last:border-0">
              <div className="min-w-0">
                <div className="font-medium">{source.name}</div>
                <div className="mt-1 truncate text-xs text-[#6d7773]">{source.path}</div>
                <div className="mt-2 text-xs text-[#6d7773]">
                  {source.documents} docs · {source.changed} changed · last scan {formatDate(source.lastScan)}
                </div>
              </div>
              <span className="text-sm text-[#56615d]">{source.provider}</span>
              <div className="flex justify-end">
                <Badge tone={statusTone(source.status)}>{source.status}</Badge>
              </div>
            </div>
          ))}
        </Panel>
      </div>
    </section>
  );
}
