import redis
import configparser as cp
from os import path

"""
 Classes implementing Rule communicators with other R2R modules:

Communicator -

Offer_Cache_Communicator -

AgreementLedger_Communicator -

Rule_Agreement_Ledger_Communicator -

Rule_Offer_Cache_Communicator -

"""


class Communicator:
    def __init__(self):
        return None


class Offer_Cache_Communicator(Communicator):
    def __init__(self):



        return None

class AgreementLedger_Communicator(Communicator):
    def __init__(self):
        main_module_name = path.splitext(path.basename(sys.modules["__main__"].__file__))[0]

        config      = cp.ConfigParser()
        config.read(f'{main_module_name}.conf')
        CACHE_HOST  = config.get('cache', 'host')
        CACHE_PORT  = config.get('cache', 'port')
        cache       = redis.Redis(host=CACHE_HOST, port=CACHE_PORT, decode_responses=True)


        return None


class Rule_Agreement_Ledger_Communicator(AgreementLedger_Communicator):
    def __init__(self):
        return None


class Rule_Offer_Cache_Communicator(Offer_Cache_Communicator):
    def __init__(self):
        return None