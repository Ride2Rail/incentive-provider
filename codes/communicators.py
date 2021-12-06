from abc import ABC, abstractmethod
import redis
import r2r_offer_utils.cache_operations
import r2r_offer_utils.advanced_logger

import configparser as cp
from os import path


class Communicator(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def accesRuleData(self) -> bool:
        pass


class AgreementLedgerCommunicator(Communicator):
    def __init__(self, data):
        super().__init__(data)

        # objects required for requests

    def accesRuleData(self) -> bool:
        # if the request was successful extract the data
        self.authenticate()
        self.obtainRequest(self.data['url_suffix'][0], self.data['values'][0])
        pass

    def authenticate(self):
        pass

    def obtainRequest(self, url_suffix, id):
        pass


class OfferCacheCommunicator(Communicator):
    def __init__(self):
        # main_module_name = path.splitext(path.basename(sys.modules["__main__"].__file__))[0]
        #
        # config = cp.ConfigParser()
        # config.read(f'{main_module_name}.conf')
        if r2r_offer_utils.advanced_logger.config is not None:
            CACHE_HOST = r2r_offer_utils.advanced_logger.config.get('cache', 'host')
            CACHE_PORT = r2r_offer_utils.advanced_logger.config.get('cache', 'port')
            cache = redis.Redis(host='localhost', port=CACHE_PORT, decode_responses=True)

            try:
                output_offer_level, output_tripleg_level = r2r_offer_utils.cache_operations.read_data_from_cache_wrapper(
                    cache,
                    "46a4fa0d-2fd2-4317-8441-1b6a9511f1e7",
                    ["bookable_total", "complete_total"],
                    ["duration", "can_share_cost"])

                print("output_offer_level = ", output_offer_level)
                print("output_tripleg_level = ", output_tripleg_level)
            except redis.exceptions.ConnectionError as exc:
                r2r_offer_utils.advanced_logger.logging.error("Reading from cache failed.")
                #response.status_code = 424
                return None






    def accesRuleData(self) -> bool:
        # if the request was successful
        pass
