import { Badge, PageHeader, Panel, SectionTitle } from "@/components/ui";

export default function SettingsPage() {
  return (
    <section className="max-w-6xl">
      <PageHeader
        title="Settings"
        description="Mock operational settings for the MVP service boundaries and deferred integrations."
      />

      <div className="mt-6 grid gap-5 lg:grid-cols-2">
        <Panel className="p-5">
          <SectionTitle title="Service endpoints" />
          <div className="mt-4 grid gap-3 text-sm">
            <SettingRow label="flora-core" value="http://localhost:8000" />
            <SettingRow label="flora-worker" value="outbox polling placeholder" />
            <SettingRow label="flora-ui" value="http://localhost:3000" />
          </div>
        </Panel>
        <Panel className="p-5">
          <SectionTitle title="Feature flags" />
          <div className="mt-4 grid gap-3 text-sm">
            <div className="flex items-center justify-between gap-4">
              <span>Automatic patch application</span>
              <Badge tone="neutral">disabled</Badge>
            </div>
            <div className="flex items-center justify-between gap-4">
              <span>Stub evidence provider</span>
              <Badge tone="good">enabled</Badge>
            </div>
            <div className="flex items-center justify-between gap-4">
              <span>Notion and GitHub Docs</span>
              <Badge tone="neutral">deferred</Badge>
            </div>
          </div>
        </Panel>
      </div>
    </section>
  );
}

function SettingRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-[#edf2ef] pb-3 last:border-0 last:pb-0">
      <span className="font-medium">{label}</span>
      <span className="text-[#56615d]">{value}</span>
    </div>
  );
}
