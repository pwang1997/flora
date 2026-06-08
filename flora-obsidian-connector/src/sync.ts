import { App, FileSystemAdapter, Notice, TFile } from 'obsidian';
import {
	FloraApiError,
	Source,
	createSource,
	createSourceDocument,
	getSources,
} from './api';
import { FloraConnectorSettings } from './settings';

interface SyncResult {
	created: number;
	skipped: number;
	failed: number;
}

interface EffectiveSyncSettings {
	floraCoreUrl: string;
	sourceName: string;
	sourcePath: string;
}

export async function syncVaultOnLoad(app: App, settings: FloraConnectorSettings): Promise<SyncResult> {
	const effectiveSettings = resolveEffectiveSettings(app, settings);
	const source = await resolveObsidianSource(effectiveSettings);
	const files = app.vault.getMarkdownFiles();
	const result: SyncResult = { created: 0, skipped: 0, failed: 0 };

	// TODO: Replace load-time full sync with periodic and event-driven note update handling.
	for (const file of files) {
		try {
			await createDocumentForFile(app, effectiveSettings.floraCoreUrl, source.id, file);
			result.created += 1;
		} catch (error) {
			if (error instanceof FloraApiError && error.status === 409) {
				// TODO: Create document versions or update source_documents when note content changes.
				result.skipped += 1;
				continue;
			}
			console.error('Failed to sync Obsidian note to Flora', file.path, error);
			result.failed += 1;
		}
	}

	return result;
}

export function showSyncResult(result: SyncResult): void {
	new Notice(
		`Flora sync complete: ${result.created} created, ${result.skipped} skipped, ${result.failed} failed.`,
	);
}

function resolveEffectiveSettings(app: App, settings: FloraConnectorSettings): EffectiveSyncSettings {
	return {
		floraCoreUrl: settings.floraCoreUrl || 'http://localhost:8000',
		sourceName: settings.sourceName || app.vault.getName(),
		sourcePath: settings.sourcePath || getVaultSourcePath(app),
	};
}

function getVaultSourcePath(app: App): string {
	const adapter = app.vault.adapter;
	if (adapter instanceof FileSystemAdapter) {
		return adapter.getBasePath();
	}
	return app.vault.getName();
}

async function resolveObsidianSource(settings: EffectiveSyncSettings): Promise<Source> {
	const sources = await getSources(settings.floraCoreUrl);
	const existingSource = findMatchingSource(sources, settings.sourcePath);
	if (existingSource) return existingSource;

	try {
		// TODO: Match source identity by user_id + source_path when flora-core supports users.
		return await createSource(settings.floraCoreUrl, {
			name: settings.sourceName,
			provider_type: 'obsidian',
			config: { source_path: settings.sourcePath },
		});
	} catch (error) {
		if (error instanceof FloraApiError && error.status === 409) {
			const refreshedSources = await getSources(settings.floraCoreUrl);
			const refreshedSource = findMatchingSource(refreshedSources, settings.sourcePath);
			if (refreshedSource) return refreshedSource;
		}
		throw error;
	}
}

function findMatchingSource(sources: Source[], sourcePath: string): Source | undefined {
	return sources.find(
		(source) =>
			source.provider_type === 'obsidian' &&
			typeof source.config.source_path === 'string' &&
			source.config.source_path === sourcePath,
	);
}

async function createDocumentForFile(
	app: App,
	floraCoreUrl: string,
	sourceId: string,
	file: TFile,
): Promise<void> {
	const content = await app.vault.read(file);
	const contentHash = await sha256Hex(content);

	// TODO: Send full content through document-version ingestion when flora-core exposes that workflow.
	await createSourceDocument(floraCoreUrl, {
		source_id: sourceId,
		external_id: file.path,
		title: file.basename,
		uri: `obsidian://open?path=${encodeURIComponent(file.path)}`,
		content_hash: contentHash,
		last_modified_at: new Date(file.stat.mtime).toISOString(),
		metadata: {
			path: file.path,
			basename: file.basename,
			extension: file.extension,
			size: file.stat.size,
			ctime: file.stat.ctime,
			mtime: file.stat.mtime,
		},
	});
}

async function sha256Hex(content: string): Promise<string> {
	const bytes = new TextEncoder().encode(content);
	const digest = await crypto.subtle.digest('SHA-256', bytes);
	return Array.from(new Uint8Array(digest))
		.map((byte) => byte.toString(16).padStart(2, '0'))
		.join('');
}
