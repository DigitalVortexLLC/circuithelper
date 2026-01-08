class ProviderRegistry:
    """
    Registry for provider sync implementations.
    """

    def __init__(self):
        self._providers = {}

    def register(self, provider_type: str, provider_class):
        """
        Register a provider sync class.

        Args:
            provider_type: Unique identifier for the provider (e.g., 'lumen', 'att')
            provider_class: Class inheriting from BaseProviderSync
        """
        self._providers[provider_type] = provider_class

    def get(self, provider_type: str):
        """
        Get a provider sync class by type.

        Args:
            provider_type: Provider identifier

        Returns:
            Provider class or None if not found
        """
        return self._providers.get(provider_type)

    def get_all(self):
        """
        Get all registered providers.

        Returns:
            Dictionary of provider_type -> provider_class
        """
        return self._providers.copy()

    def unregister(self, provider_type: str):
        """
        Unregister a provider.

        Args:
            provider_type: Provider identifier
        """
        if provider_type in self._providers:
            del self._providers[provider_type]


# Global provider registry instance
provider_registry = ProviderRegistry()
