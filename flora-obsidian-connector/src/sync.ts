import { App, FileSystemAdapter, Notice, TFile } from 'obsidian';
import {
	FloraApiError,
	createDocumentVersion,
	createSource,
	createSourceDocument,
	getSources,
	listSourceDocuments,
} from './api.js';
import type { Source, SourceDocument } from './api.js';
import type { FloraConnectorSettings } from './settings.js';

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
	const existingDocuments = await listSourceDocuments(effectiveSettings.floraCoreUrl, source.id);
	const files = app.vault.getMarkdownFiles();
	const result: SyncResult = { created: 0, skipped: 0, failed: 0 };

	// TODO: Replace load-time full sync with periodic and event-driven note update handling.
	for (const file of files) {
		try {
			const document = await resolveSourceDocumentForFile(
				effectiveSettings.floraCoreUrl,
				source.id,
				file,
				existingDocuments,
			);
			await createVersionForFile(app, effectiveSettings.floraCoreUrl, document.id, file);
			result.created += 1;
		} catch (error) {
			if (error instanceof FloraApiError && error.status === 409) {
				// TODO: Compare latest document version before deciding whether to create updated versions.
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
	floraCoreUrl: string,
	sourceId: string,
	file: TFile,
): Promise<SourceDocument> {
	return await createSourceDocument(floraCoreUrl, {
		source_id: sourceId,
		external_id: file.path,
		title: file.basename,
		uri: `obsidian://open?path=${encodeURIComponent(file.path)}`,
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

async function resolveSourceDocumentForFile(
	floraCoreUrl: string,
	sourceId: string,
	file: TFile,
	existingDocuments: SourceDocument[],
): Promise<SourceDocument> {
	const existingDocument = existingDocuments.find((document) => document.external_id === file.path);
	if (existingDocument) return existingDocument;

	try {
		const createdDocument = await createDocumentForFile(floraCoreUrl, sourceId, file);
		existingDocuments.push(createdDocument);
		return createdDocument;
	} catch (error) {
		if (error instanceof FloraApiError && error.status === 409) {
			const refreshedDocuments = await listSourceDocuments(floraCoreUrl, sourceId);
			const refreshedDocument = refreshedDocuments.find((document) => document.external_id === file.path);
			if (refreshedDocument) return refreshedDocument;
		}
		throw error;
	}
}

async function createVersionForFile(
	app: App,
	floraCoreUrl: string,
	documentId: string,
	file: TFile,
): Promise<void> {
	const content = await app.vault.read(file);
	const contentHash = await sha256Hex(content);

	// TODO: Use updated/deleted/restored change types when event-driven note updates are implemented.
	await createDocumentVersion(floraCoreUrl, {
		document_id: documentId,
		content,
		content_hash: contentHash,
		change_type: 'created',
	});
}

async function sha256Hex(content: string): Promise<string> {
	const bytes = new TextEncoder().encode(content);
	const digest = await crypto.subtle.digest('SHA-256', bytes);
	return Array.from(new Uint8Array(digest))
		.map((byte) => byte.toString(16).padStart(2, '0'))
		.join('');
}
