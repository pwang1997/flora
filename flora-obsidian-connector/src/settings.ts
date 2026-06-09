import { App, PluginSettingTab, Setting } from 'obsidian';
import type FloraConnectorPlugin from './main.js';

export interface FloraConnectorSettings {
	floraCoreUrl: string;
	sourcePath: string;
	sourceName: string;
}

export const DEFAULT_SETTINGS: FloraConnectorSettings = {
	floraCoreUrl: 'http://localhost:8000',
	sourcePath: '',
	sourceName: '',
};

export class FloraConnectorSettingTab extends PluginSettingTab {
	plugin: FloraConnectorPlugin;

	constructor(app: App, plugin: FloraConnectorPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const { containerEl } = this;

		containerEl.empty();

		new Setting(containerEl)
			.setName('Flora core URL')
			.setDesc('The base URL for flora-core.')
			.addText((text) =>
				text
					.setValue(this.plugin.settings.floraCoreUrl)
					.onChange(async (value) => {
						this.plugin.settings.floraCoreUrl = value.trim();
						await this.plugin.saveSettings();
					}),
			);

		new Setting(containerEl)
			.setName('Source path')
			.setDesc('Leave blank to use the local vault path.')
			.addText((text) =>
				text
					.setPlaceholder('/path/to/vault')
					.setValue(this.plugin.settings.sourcePath)
					.onChange(async (value) => {
						this.plugin.settings.sourcePath = value.trim();
						await this.plugin.saveSettings();
					}),
			);

		new Setting(containerEl)
			.setName('Source name')
			.setDesc('Leave blank to use the vault name.')
			.addText((text) =>
				text
					.setPlaceholder('My Obsidian vault')
					.setValue(this.plugin.settings.sourceName)
					.onChange(async (value) => {
						this.plugin.settings.sourceName = value.trim();
						await this.plugin.saveSettings();
					}),
			);
	}
}
