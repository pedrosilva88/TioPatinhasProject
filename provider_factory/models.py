from configs.models import Provider
from typing import Any

class ProviderClient:
    provider: Provider
    session: Any

class ProviderController:
    provider: Provider
    runner: Any