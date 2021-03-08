from dataclasses import dataclass

@dataclass
class Strategy:
    def run(self):
        """
        Override This method
        """

    def shouldGetStockEarnings(self):
        """
        Override This method
        """