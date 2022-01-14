import codes.rules
import codes.communicators as communicators
import logging

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

    def consistencyCheck(self, allIncentives):
        #
        # currently this is only a placeholder
        #
        return allIncentives

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
                    offer_dict[offer_id][incentive_name] = rule.offer_dict[offer_id].eligible
                except KeyError as ke:
                    logging.error(f"Missing result for offer {offer_id} when processing rule {rule.name} "
                                  f"in the IncentiveProvider class")

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
        # create incentive provider rules
        #
        # create rule RideSharingInvolved
        self.ruleRideSharingInvolved = codes.rules.RideSharingInvolved({"offer_cache_communicator": OCC})
        # create rule ruleTwoPassShared
        self.ruleTwoPassShared = codes.rules.TwoPassShared(communicator_dict)
        self.ruleThreePreviousEpisodesRS = codes.rules.ThreePreviousEpisodesRS(communicator_dict)

        #
        # insert all created rules into the rule_list
        #
        rule_list = [self.ruleRideSharingInvolved, self.ruleTwoPassShared, self.ruleThreePreviousEpisodesRS]

        #
        # create Incentive Provider
        #
        self.incentiveProvider = IncentiveProvider(rule_list)

    def getIncentives(self, data_dict):
        allIncentives = self.incentiveProvider.getEligibleIncentives(data_dict)
        return self.incentiveProvider.consistencyCheck(allIncentives)


class TravelOfferIterator:
    def __init__(self):
        pass
