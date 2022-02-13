import collections

import codes.rules
import codes.communicators as communicators
import logging
from functools import wraps

logger = logging.getLogger('incentive_provider_api.incentive_provider')


class IncentiveProvider:
    def __init__(self, ruleList):
        self.ruleList = ruleList

    def getEligibleIncentives(self, data_dict):
        """
        Checks the fulfillment of the rules and reshapes them into offer_id - rule format
        :param data_dict: dictionary with data, usually request_id
        :return: dictionary of offers
        """

        # get all offer ids
        for rule in self.ruleList:
            # check the rule fulfilement
            rule.isFulfilled(data_dict)
        return self.reshapeRuleDicts()

    def incentiveIterWrapper(fun):
        @wraps(fun)
        def wrap(self, allIncentives):
            for key in allIncentives.keys():
                for incentive_name in allIncentives[key].keys():
                    # check if there is a higher priority rule and if it is eligible, set the lesser rule eligibility
                    # to false
                    try:
                        fun(self, allIncentives, key, incentive_name)
                    except KeyError as ke:
                        logger.error(f"Key missing in Incentive provider: {ke}")
            return allIncentives
        return wrap

    @incentiveIterWrapper #decorator ensures calling of the function on every offer item and incentive and logging of errors
    def consistencyCheck(self, allIncentives, key, incentive_name):
        """
        cancel the incentive if there was assigned subordinate incentive that is not compatible with this one
        """
        if allIncentives[key][incentive_name].incentiveAbove is not None and \
                allIncentives[key][allIncentives[key][incentive_name].incentiveAbove].eligible:
            allIncentives[key][incentive_name].eligible = False

    @incentiveIterWrapper #decorator ensures calling of the function on every offer item and incentive and logging of errors
    def extractBooleanValues(self, allIncentives, key, incentive_name):
        """
        replaces the incentive with its boolean value
        it is done as the last step before outputting the results of the incentive pre-evaluation
        as only boolean values are sufficient to be outputted
        """
        allIncentives[key][incentive_name] = allIncentives[key][incentive_name].eligible

    def reshapeRuleDicts(self):
        """
        Reshapes the rule dictionaries from dictionary for each rule, to one dictionary with incentives for offer_ids
        :return: dictionary of offer_id : incentive_eligibility dictionaries
        """
        # set of offer ids
        offer_ids = set()

        for rule in self.ruleList:
            # add the Rule's offer_ids to the list
            offer_ids.update(set(rule.offer_dict.keys()))
        # dictionary of offers
        offer_dict = {}
        # iterate the offers and assign incentives to each offer
        for offer_id in offer_ids:
            offer_dict[offer_id] = {}
            # go through each rule and assign the incentive to the offer
            for rule in self.ruleList:
                try:
                    # extract incentive name
                    incentive_name = rule.offer_dict[offer_id].incentiveRankerID
                    # add the rule for the given offer_id under the incentive name to the dictionary
                    offer_dict[offer_id][incentive_name] = rule.offer_dict[offer_id]
                except KeyError as ke:
                    logger.error(f"Missing result for offer {offer_id} when processing rule {rule.name} "
                                  f"in the IncentiveProvider class")
        return offer_dict

    def flatten_incentives(self, incentive_dict, occ: communicators.OfferCacheCommunicator, request_id):
        parent_key = f"{request_id}:incentives"
        flat_dict = IncentiveProvider.flatten(incentive_dict, parent_key)
        return occ.write_dict_redis(flat_dict)

    @staticmethod
    def flatten(d: dict, parent_key='', sep=':'):
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + str(k) if parent_key else k
            if isinstance(v, collections.abc.MutableMapping):
                items.extend(IncentiveProvider.flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


class IncentiveProviderManager:
    def __init__(self, config):
        #
        # create required communicators
        #
        # offer cache communicator
        self.OCC = communicators.OfferCacheCommunicator(config)
        self.ALC = communicators.AgreementLedgerCommunicator(config)

        communicator_dict = {
            "AL_communicator": self.ALC,
            "offer_cache_communicator": self.OCC
        }

        #
        # create incentive provider incentives
        #
        incentiveTrainSeatUpgrade = codes.rules.Incentive("trainSeatUpgrade", "Train seat upgrade")
        incentive10discount = codes.rules.Incentive("10discount", "10% discount", "20discount")
        incentive20discount = codes.rules.Incentive("20discount", "20% discount")
        #
        # create incentive provider rules
        #
        ruleRideSharingInvolved = codes.rules.RideSharingInvolved({"offer_cache_communicator": self.OCC}, incentive10discount)
        ruleTwoPassShared = codes.rules.TwoPassShared(communicator_dict, incentiveTrainSeatUpgrade)
        ruleThreePreviousEpisodesRS = codes.rules.ThreePreviousEpisodesRS(communicator_dict, incentive20discount)

        #
        # insert all created rules into the rule_list
        #
        self.rule_list = [ruleRideSharingInvolved, ruleTwoPassShared, ruleThreePreviousEpisodesRS]

        #
        # create Incentive Provider
        #
        self.incentiveProvider = IncentiveProvider(self.rule_list)

    def getIncentives(self, data_dict):
        allIncentives = self.incentiveProvider.getEligibleIncentives(data_dict)
        allIncentives = self.incentiveProvider.consistencyCheck(allIncentives)
        return self.incentiveProvider.extractBooleanValues(allIncentives)

    def incentivesToCache(self, data_dict, request_id):
        return self.incentiveProvider.flatten_incentives(data_dict, self.OCC, request_id)