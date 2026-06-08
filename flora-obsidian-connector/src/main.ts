import { Notice, Plugin } from 'obsidian';
import {
	DEFAULT_SETTINGS,
	FloraConnectorSettingTab,
	FloraConnectorSettings,
} from './settings';
import { showSyncResult, syncVaultOnLoad } from './sync';

export default class FloraConnectorPlugin extends Plugin {
	settings!: FloraConnectorSettings;

	async onload() {
		await this.loadSettings();
		this.addSettingTab(new FloraConnectorSettingTab(this.app, this));

		try {
			const result = await syncVaultOnLoad(this.app, this.settings);
			showSyncResult(result);
		} catch (error) {
			console.error('Failed to sync Obsidian vault to Flora', error);
			new Notice(`Flora sync failed: ${error instanceof Error ? error.message : 'unknown error'}`);
		}
	}

	onunload() {}

	async loadSettings() {
		const storedSettings = (await this.loadData()) as Partial<FloraConnectorSettings> | null;
		this.settings = {
			...DEFAULT_SETTINGS,
			...storedSettings,
		};
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}
}
