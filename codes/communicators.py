from abc import ABC, abstractmethod
import redis
import configparser as cp
from os import path


class Communicator(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def checkRule(self) -> bool:
        pass


class AgreementLedgerCommunicator(Communicator):
    def __init__(self, data):
        super().__init__(data)

        # objects required for requests

    def checkRule(self) -> bool:
        # if the request was successful extract the data
        self.authenticate()
        self.obtainRequest(self.data['url_suffix'][0], self.data['values'][0])
        pass

    def authenticate(self):
        pass

    def obtainRequest(self, url_suffix, id):
        pass


class OfferCacheCommunicator(Communicator):
    def __init__(self, data, config):
        # main_module_name = path.splitext(path.basename(sys.modules["__main__"].__file__))[0]
        #
        # config = cp.ConfigParser()
        # config.read(f'{main_module_name}.conf')
        if config is not None:
            CACHE_HOST = config.get('cache', 'host')
            CACHE_PORT = config.get('cache', 'port')
            cache = redis.Redis(host=CACHE_HOST, port=CACHE_PORT, decode_responses=True)

    def checkRule(self) -> bool:
        # if the request was successful
        pass
