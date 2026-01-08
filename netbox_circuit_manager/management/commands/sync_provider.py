from django.core.management.base import BaseCommand
from netbox_circuit_manager.models import ProviderAPIConfig
from netbox_circuit_manager.providers import provider_registry


class Command(BaseCommand):
    help = 'Synchronize circuit data from provider APIs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--provider',
            type=str,
            help='Specific provider ID to sync (optional)',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test connection only, do not sync',
        )

    def handle(self, *args, **options):
        provider_id = options.get('provider')
        test_only = options.get('test', False)

        # Get API configurations to sync
        if provider_id:
            configs = ProviderAPIConfig.objects.filter(pk=provider_id, sync_enabled=True)
        else:
            configs = ProviderAPIConfig.objects.filter(sync_enabled=True)

        if not configs.exists():
            self.stdout.write(self.style.WARNING('No enabled provider configurations found'))
            return

        for config in configs:
            self.stdout.write(f'\nProcessing provider: {config.provider.name} ({config.provider_type})')

            # Get provider sync class
            provider_class = provider_registry.get(config.provider_type)
            if not provider_class:
                self.stdout.write(
                    self.style.ERROR(f'Provider type "{config.provider_type}" not found in registry')
                )
                continue

            # Initialize provider sync
            provider_sync = provider_class(config)

            if test_only:
                # Test connection
                self.stdout.write('Testing connection...')
                result = provider_sync.test_connection()

                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Connection successful (response time: {result['response_time']:.2f}s)"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"Connection failed: {result['message']}")
                    )
            else:
                # Perform sync
                self.stdout.write('Starting synchronization...')
                stats = provider_sync.sync_all()

                # Display results
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Sync complete: {stats['success']}/{stats['total']} circuits synced"
                    )
                )

                if stats['failed'] > 0:
                    self.stdout.write(
                        self.style.WARNING(f"Failed: {stats['failed']}")
                    )

                if stats['errors']:
                    self.stdout.write(self.style.ERROR('\nErrors:'))
                    for error in stats['errors']:
                        self.stdout.write(f"  - {error}")

        self.stdout.write(self.style.SUCCESS('\nDone!'))
