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
            try:
                for key in allIncentives.keys():
                    for incentive_name in allIncentives[key].keys():
                        # check if there is a higher priority rule and if it is eligible, set the lesser rule eligibility
                        # to false
                        fun(self, allIncentives, key, incentive_name)
            except KeyError as ke:
                logger.error(f"Key missing in Incentive provider: {ke}")
            return allIncentives
        return wrap

    @incentiveIterWrapper
    def consistencyCheck(self, allIncentives, key, incentive_name):
        """
        replaces the incentive with its boolean value
        """
        if allIncentives[key][incentive_name].incentiveAbove is not None and \
                allIncentives[key][allIncentives[key][incentive_name].incentiveAbove].eligible:
            allIncentives[key][incentive_name].eligible = False

    @incentiveIterWrapper
    def extractBooleanValues(self, allIncentives, key, incentive_name):
        """
        replaces the incentive with its boolean value
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
                    incentive_name = rule.offer_dict[offer_id].incentiveRankerID
                    offer_dict[offer_id][incentive_name] = rule.offer_dict[offer_id] #.eligible
                except KeyError as ke:
                    logging.error(f"Missing result for offer {offer_id} when processing rule {rule.name} "
                                  f"in the IncentiveProvider class")
        return offer_dict

class IncentiveProviderManager:
    def __init__(self, config):
        #
        # create required communicators
        #
        # offer cache communicator
        OCC = communicators.OfferCacheCommunicator(config)
        ALC = communicators.AgreementLedgerCommunicator(config)

        communicator_dict = {
            "AL_communicator": ALC,
            "offer_cache_communicator": OCC
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
        ruleRideSharingInvolved = codes.rules.RideSharingInvolved({"offer_cache_communicator": OCC}, incentive10discount)
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

class TravelOfferIterator:
    def __init__(self):
        pass
