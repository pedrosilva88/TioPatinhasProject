from datetime import datetime
from models.base_models import Contract, Event

class ContractOPGInfo(Contract):
    lastExecution: datetime
    averageVolume: float
    volumeFirstMinute: float

    # TODO Preciso de ver para que preciso destas 3 variables e fazer a conversão delas para modelos meus
    # realTimeBarList: RealTimeBarList
    # contractDetails: ContractDetails
    # priceRules: [PriceIncrement]

    def __init__(self, contract: Contract, lastExecution: datetime = None, 
                        averageVolume: float = None, volumeFirstMinute: float = None):
                        # realTimeBarList: RealTimeBarList = None, contractDetails: ContractDetails = None, 
                        # priceRules: [PriceIncrement] = None):
        Contract.__init__(self, symbol= contract.symbol, country= contract.country, exchange= contract.exchange)
        self.lastExecution = lastExecution
        self.averageVolume = averageVolume
        self.volumeFirstMinute = volumeFirstMinute

        # self.realTimeBarList = realTimeBarList
        # self.contractDetails = contractDetails
        # self.priceRules = priceRules

class EventOPG(Event):
    def __init__(self, contract: Contract, 
                        datetime: datetime, 
                        open: float, 
                        close: float, 
                        high: float, 
                        low: float, 
                        volume: float, zigzag: bool, rsi: float, lastPrice = None):
        Event.__init__(self, contract= contract, datetime= datetime,
                        open= open, close= close, high= high, low= low, volume= volume)