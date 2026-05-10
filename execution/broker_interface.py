from abc import (
    ABC,
    abstractmethod
)

# =========================================================
# ABSTRACT BROKER
# =========================================================

class BrokerInterface(ABC):

    @abstractmethod
    def connect(self):

        pass

    @abstractmethod
    def get_balance(self):

        pass

    @abstractmethod
    def place_order(

        self,

        symbol,

        quantity,

        side
    ):

        pass

    @abstractmethod
    def positions(self):

        pass