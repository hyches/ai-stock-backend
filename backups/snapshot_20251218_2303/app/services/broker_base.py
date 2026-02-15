from abc import ABC, abstractmethod

class BrokerBase(ABC):
    @abstractmethod
    async def login(self, *args, **kwargs):
        pass

    @abstractmethod
    async def place_order(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_portfolio(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_quote(self, *args, **kwargs):
        pass 