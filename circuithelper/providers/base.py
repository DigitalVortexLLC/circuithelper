from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
import requests
from circuits.models import Circuit


class BaseProviderSync(ABC):
    """
    Base class for provider API integrations.

    Subclass this to create integrations with specific carrier APIs.
    """

    # Provider identifier - must be unique
    provider_name: str = None

    def __init__(self, api_config):
        """
        Initialize the provider sync with API configuration.

        Args:
            api_config: ProviderAPIConfig instance
        """
        self.config = api_config
        self.api_endpoint = api_config.api_endpoint
        self.api_key = api_config.api_key
        self.api_secret = api_config.api_secret
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        """
        Configure the requests session with authentication headers.
        Override this method to customize session setup.
        """
        if self.api_key:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the provider API.

        Returns:
            True if authentication successful, False otherwise
        """
        pass

    @abstractmethod
    def get_circuits(self) -> List[Dict]:
        """
        Retrieve list of circuits from provider API.

        Returns:
            List of circuit data dictionaries
        """
        pass

    @abstractmethod
    def get_circuit_details(self, circuit_id: str) -> Dict:
        """
        Get detailed information for a specific circuit.

        Args:
            circuit_id: Provider's circuit identifier

        Returns:
            Dictionary containing circuit details
        """
        pass

    @abstractmethod
    def sync_circuit_costs(self, circuit: Circuit, provider_data: Dict) -> bool:
        """
        Sync cost information (NRC/MRC) for a circuit.

        Args:
            circuit: NetBox Circuit instance
            provider_data: Data from provider API

        Returns:
            True if sync successful
        """
        pass

    def sync_circuit_tickets(self, circuit: Circuit, provider_data: Dict) -> bool:
        """
        Sync ticket information for a circuit.
        Optional method - override if provider supports ticket API.

        Args:
            circuit: NetBox Circuit instance
            provider_data: Data from provider API

        Returns:
            True if sync successful
        """
        return True

    def sync_circuit_path(self, circuit: Circuit, provider_data: Dict) -> bool:
        """
        Sync circuit path/route information.
        Optional method - override if provider supports path data.

        Args:
            circuit: NetBox Circuit instance
            provider_data: Data from provider API

        Returns:
            True if sync successful
        """
        return True

    def sync_all(self) -> Dict[str, int]:
        """
        Perform full synchronization of all circuits.

        Returns:
            Dictionary with sync statistics:
            {
                'total': int,
                'success': int,
                'failed': int,
                'errors': List[str]
            }
        """
        stats = {"total": 0, "success": 0, "failed": 0, "errors": []}

        try:
            # Authenticate
            if not self.authenticate():
                stats["errors"].append("Authentication failed")
                return stats

            # Get circuits from provider
            circuits_data = self.get_circuits()
            stats["total"] = len(circuits_data)

            # Sync each circuit
            for circuit_data in circuits_data:
                try:
                    # Find matching NetBox circuit
                    circuit = self._match_circuit(circuit_data)
                    if not circuit:
                        stats["failed"] += 1
                        stats["errors"].append(
                            f"Circuit not found: {circuit_data.get('id', 'unknown')}"
                        )
                        continue

                    # Get detailed circuit information
                    details = self.get_circuit_details(circuit_data["id"])

                    # Sync costs
                    self.sync_circuit_costs(circuit, details)

                    # Sync tickets (optional)
                    self.sync_circuit_tickets(circuit, details)

                    # Sync path (optional)
                    self.sync_circuit_path(circuit, details)

                    stats["success"] += 1

                except Exception as e:
                    stats["failed"] += 1
                    stats["errors"].append(f"Error syncing circuit: {str(e)}")

            # Update last sync timestamp
            self.config.last_sync = datetime.now()
            self.config.sync_status = f"Success: {stats['success']}/{stats['total']}"
            self.config.save()

        except Exception as e:
            stats["errors"].append(f"Sync failed: {str(e)}")
            self.config.sync_status = f"Failed: {str(e)}"
            self.config.save()

        return stats

    def _match_circuit(self, provider_data: Dict) -> Optional[Circuit]:
        """
        Match provider circuit data to a NetBox circuit.
        Override this method to customize matching logic.

        Args:
            provider_data: Circuit data from provider

        Returns:
            Matching Circuit instance or None
        """
        # Default: match by circuit ID (cid)
        provider_cid = provider_data.get("cid") or provider_data.get("circuit_id")
        if provider_cid:
            try:
                return Circuit.objects.get(cid=provider_cid)
            except Circuit.DoesNotExist:
                pass

        return None

    def test_connection(self) -> Dict[str, any]:
        """
        Test the API connection and authentication.

        Returns:
            Dictionary with connection test results:
            {
                'success': bool,
                'message': str,
                'response_time': float (seconds)
            }
        """
        start_time = datetime.now()

        try:
            if self.authenticate():
                elapsed = (datetime.now() - start_time).total_seconds()
                return {
                    "success": True,
                    "message": "Connection successful",
                    "response_time": elapsed,
                }
            else:
                return {"success": False, "message": "Authentication failed", "response_time": 0}
        except Exception as e:
            return {"success": False, "message": f"Connection error: {str(e)}", "response_time": 0}
