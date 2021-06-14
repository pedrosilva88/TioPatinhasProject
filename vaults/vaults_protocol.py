from provider_factory.models import ProviderController

class VaultsControllerProtocol:
    @property
    def controller(self) -> ProviderController:
        pass
