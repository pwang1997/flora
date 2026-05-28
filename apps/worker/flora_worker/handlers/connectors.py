from flora_connectors import LocalMarkdownConnector
from flora_shared.enums import ProviderType


def connector_for(provider_type: str) -> LocalMarkdownConnector:
    if provider_type in {ProviderType.LOCAL_MARKDOWN, ProviderType.OBSIDIAN}:
        return LocalMarkdownConnector()
    raise ValueError(f"Unsupported provider type: {provider_type}")
