from abc import ABC, abstractmethod
import redis
import r2r_offer_utils.cache_operations
import logging

import configparser as cp
from os import path


logger = logging.getLogger('incentive_provider_api.communicators')


########################################################################################################################
########################################################################################################################
########################################################################################################################
class Communicator(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def accessRuleData(self) -> bool:
        pass

########################################################################################################################
########################################################################################################################
########################################################################################################################
class AgreementLedgerCommunicator(Communicator):
    def __init__(self, data):
        super().__init__(data)

        # objects required for requests

    def accessRuleData(self) -> bool:
        # if the request was successful extract the data
        self.authenticate()
        self.obtainRequest(self.data['url_suffix'][0], self.data['values'][0])
        pass

    def authenticate(self):
        pass

    def obtainRequest(self, url_suffix, id):
        pass
########################################################################################################################
########################################################################################################################
########################################################################################################################
"""
class ensuring communication with the offer Cache
"""
class OfferCacheCommunicator(Communicator):

    """
        Establish connection with the offer cache.
    """
    def __init__(self):
        if r2r_offer_utils.advanced_logger.config is not None:
            # read connection parameters from the config file
            CACHE_HOST      = r2r_offer_utils.advanced_logger.config.get('cache', 'host')
            CACHE_PORT      = r2r_offer_utils.advanced_logger.config.get('cache', 'port')

            logger.info(f"Connecting to offer cache: CACHE_HOST = {CACHE_HOST}, CACHE_PORT = {CACHE_PORT}")
            try:
                # establish connection to the offer cache
                self.cache           = redis.Redis(host=CACHE_HOST, port=CACHE_PORT, decode_responses=True)
            except redis.exceptions.ConnectionError as exc:
                logger.error("Connection to the offer cache has not been established.")
                return None
        else:
            logger.error('Could not read config file in communicators.py')
            return None

    """
        Request data from the offer cache.
    """
    def read_data_from_offer_cache(self, request_id, list_offer_level_keys, list_tripleg_level_keys):
        try:
            # read data from the offer cache
            logger.info(f"Read data from the offer cache: request_id = {request_id}, list_offer_level_keys = {list_offer_level_keys}, list_tripleg_level_keys = {list_tripleg_level_keys}")
            output_offer_level, output_tripleg_level = r2r_offer_utils.cache_operations.read_data_from_cache_wrapper(
                self.cache,
                request_id,
                list_offer_level_keys,
                list_tripleg_level_keys)
        except redis.exceptions.ConnectionError as exc:
            logger.error("Reading from the offer cache failed in communicators.py.")
            return None
        return {'output_offer_level':output_offer_level, 'output_tripleg_level':output_tripleg_level}


    def accessRuleData(self) -> bool:
        # if the request was successful
        pass
