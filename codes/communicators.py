from abc import ABC, abstractmethod
import redis
import r2r_offer_utils.cache_operations
import logging

from codes.AL_requester import *

logger = logging.getLogger('incentive_provider_api.communicators')


########################################################################################################################
########################################################################################################################
########################################################################################################################
class Communicator(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def accessRuleData(self, dict_data):
        pass


########################################################################################################################
########################################################################################################################
########################################################################################################################
class AgreementLedgerCommunicator(Communicator):
    def __init__(self, data):
        super().__init__(data)
        config = data["config"]
        # objects required for requests
        self.url_dict = {
            "disc20_url": config.get('agreement_ledger_api', 'disc20_url'),
            "upgrSeat_url": config.get('agreement_ledger_api', 'upgrSeat_url')
        }
        self.requestObtainer = RequestObtainer(config, "AgreementLedgerObtainer")

    def accessRuleData(self, dict_data):
        # obtain the data from Agreement ledger using request obtainer
        url = self.url_dict[dict_data['url']]
        return self.requestObtainer.load_request(url, dict_data['id'])


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

    def __init__(self, config, data):
        # get the ports
        super().__init__(data)
        if config is not None:
            # read connection parameters from the config file
            CACHE_HOST = config.get('cache', 'host')
            CACHE_PORT = config.get('cache', 'port')
            logger.info(f"Connecting to offer cache: CACHE_HOST = {CACHE_HOST}, CACHE_PORT = {CACHE_PORT}")
            try:
                # establish connection to the offer cache
                self.cache = redis.Redis(host=CACHE_HOST, port=CACHE_PORT, decode_responses=True)
            except redis.exceptions.ConnectionError as exc:
                logger.error("Connection to the offer cache has not been established.")
        else:
            logger.error('Could not read config file in communicators.py')

    """
     Request data from the offer cache.
    """
    def read_data_from_offer_cache(self, request_id, list_offer_level_keys, list_tripleg_level_keys):
        try:
            # read data from the offer cache
            logger.info(f"Read data from the offer cache: request_id = {request_id},"
                        f"list_offer_level_keys = {list_offer_level_keys}, "
                        f"list_tripleg_level_keys = {list_tripleg_level_keys}")
            output_offer_level, output_tripleg_level = r2r_offer_utils.cache_operations.read_data_from_cache_wrapper(
                self.cache,
                request_id,
                list_offer_level_keys,
                list_tripleg_level_keys)
        except redis.exceptions.ConnectionError as exc:
            logger.error(f"Reading from the offer cache failed in communicators.py: {str(exc)}")
            return None
        return {'output_offer_level': output_offer_level, 'output_tripleg_level': output_tripleg_level}

    def accessRuleData(self, dict_data):
        request_id = dict_data['request_id']
        # if its a call for more complicated data
        if 'list_offer_level_keys' in dict_data:
            list_offer_level_keys = dict_data['list_offer_level_keys']
            list_tripleg_level_keys = dict_data['list_tripleg_level_keys']
            return self.read_data_from_offer_cache(request_id, list_offer_level_keys, list_tripleg_level_keys)
        # if its a simple call
        else:
            try:
                pipe = self.cache.pipeline()
                pipe.lrange(f"{request_id}:offers", 0, -1)
                pipe.get(f"{request_id}:{dict_data['offer_level_id']}")
                pipe_list = pipe.execute()
                pipe_res_dict = {
                    "offer_ids": pipe_list[0],
                    "traveller_id": pipe_list[1]
                }
                return pipe_res_dict
            except KeyError:
                return None
            except redis.exceptions.ConnectionError as exc:
                logging.debug("Reading from cache by a feature collector failed")
