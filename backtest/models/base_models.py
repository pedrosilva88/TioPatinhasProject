class BacktestItem:
    event: Event

    def __init__(self, contract: Contract, 
                        datetime: datetime, 
                        open: float,
                        close: float,
                        high: float,
                        low: float,
                        volume: float) -> None:
        self.event = Event(contract= contract, datetime=datetime, 
                            open=open, close=close, high=high, low=low, volume=volume)