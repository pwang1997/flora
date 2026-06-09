import { requestUrl } from 'obsidian';

type ApiErrorDetail = string | { msg?: string } | Array<{ msg?: string }>;

export type HealthResponse = {
	status: string;
};

export interface Source {
	id: string;
	name: string;
	provider_type: 'obsidian';
	config: Record<string, unknown>;
	status: string;
	document_count: number;
	changed_count: number;
	last_scan_at: string | null;
}

export interface SourceCreateRequest {
	name: string;
	provider_type: 'obsidian';
	config: {
		source_path: string;
	};
}

export interface SourceDocument {
	id: string;
	source_id: string;
	external_id: string;
	title: string;
	uri: string | null;
	metadata: Record<string, unknown>;
}

export interface SourceDocumentCreateRequest {
	source_id: string;
	external_id: string;
	title: string;
	uri: string;
	last_modified_at: string | null;
	metadata: Record<string, unknown>;
}

export interface DocumentVersion {
	id: string;
	document_id: string;
	content_hash: string;
	content: string;
	change_type: 'created' | 'updated' | 'deleted' | 'restored';
	version_number: number;
	created_at: string;
}

export interface DocumentVersionCreateRequest {
	document_id: string;
	content_hash: string;
	content: string;
	change_type: 'created' | 'updated' | 'deleted' | 'restored';
}

export class FloraApiError extends Error {
	status: number;

	constructor(status: number, message: string) {
		super(message);
		this.name = 'FloraApiError';
		this.status = status;
	}
}

interface FloraRequestInit {
	method?: string;
	body?: string;
	headers?: Record<string, string>;
}

function formatApiError(status: number, detail: ApiErrorDetail | undefined): string {
	if (typeof detail === 'string') return detail;
	if (Array.isArray(detail)) {
		const messages = detail.map((item) => item.msg).filter(Boolean);
		if (messages.length > 0) return messages.join(', ');
	}
	if (detail && typeof detail === 'object' && 'msg' in detail && detail.msg) {
		return detail.msg;
	}
	return `API request failed: ${status}`;
}

function buildUrl(baseUrl: string, path: string): string {
	const normalizedBaseUrl = baseUrl.replace(/\/+$/, '');
	const normalizedPath = path.startsWith('/') ? path : `/${path}`;
	return `${normalizedBaseUrl}${normalizedPath}`;
}

async function fetchJson<T>(baseUrl: string, path: string, init?: FloraRequestInit): Promise<T> {
	const response = await requestUrl({
		url: buildUrl(baseUrl, path),
		method: init?.method ?? 'GET',
		contentType: 'application/json',
		body: init?.body,
		headers: {
			'Content-Type': 'application/json',
			...init?.headers,
		},
		throw: false,
	});
	if (response.status < 200 || response.status >= 300) {
		let detail: ApiErrorDetail | undefined;
		if (isApiErrorResponse(response.json)) {
			detail = response.json.detail;
		}
		throw new FloraApiError(response.status, formatApiError(response.status, detail));
	}
	return response.json as T;
}

function isApiErrorResponse(value: unknown): value is { detail?: ApiErrorDetail } {
	return typeof value === 'object' && value !== null && 'detail' in value;
}

export function getHealth(baseUrl: string) {
	return fetchJson<HealthResponse>(baseUrl, '/health');
}

export function getSources(baseUrl: string) {
	return fetchJson<Source[]>(baseUrl, '/v1/sources/list');
}

export function createSource(baseUrl: string, payload: SourceCreateRequest) {
	return fetchJson<Source>(baseUrl, '/v1/sources/create', {
		method: 'POST',
		body: JSON.stringify(payload),
	});
}

export function createSourceDocument(baseUrl: string, payload: SourceDocumentCreateRequest) {
	return fetchJson<SourceDocument>(baseUrl, '/v1/source-documents/create', {
		method: 'POST',
		body: JSON.stringify(payload),
	});
}

export function listSourceDocuments(baseUrl: string, sourceId: string) {
	return fetchJson<SourceDocument[]>(
		baseUrl,
		`/v1/source-documents/list?source_id=${encodeURIComponent(sourceId)}`,
	);
}

export function createDocumentVersion(baseUrl: string, payload: DocumentVersionCreateRequest) {
	return fetchJson<DocumentVersion>(baseUrl, '/v1/document-versions/create', {
		method: 'POST',
		body: JSON.stringify(payload),
	});
}
