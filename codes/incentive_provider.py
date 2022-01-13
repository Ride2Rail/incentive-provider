from codes.rules import *
import codes.communicators as communicators
import logging

logger = logging.getLogger('incentive_provider_api.incentive_provider')

class IncentiveProvider:
    def __init__(self, ruleList):
        self.ruleList = ruleList

    def getEligibleIncentives(self, data_dict):
        #
        # apply all rules in the ruleList
        #
        return [rule.isFulfilled(data_dict) for rule in self.ruleList]

    def consistencyCheck(self, allIncentives):
        #
        # currently this is only a placeholder
        #
        return allIncentives


class IncentiveProviderManager:
    def __init__(self, config):
        #
        # create required communicators
        #
        # offer cache communicator
        OCC = communicators.OfferCacheCommunicator(config)
        ALC = communicators.AgreementLedgerCommunicator(config)
        #
        # create incentive provider rules
        #
        # create rule RideSharingInvolved
        self.ruleRideSharingInvolved = RideSharingInvolved({"offer_cache_communicator": OCC})
        # create rule ruleTwoPassShared
        self.ruleTwoPassShared = TwoPassShared({"AL_communicator": ALC})

        #self.threeBookingRS = ThreePreviousEpisodesRS(self.agreementRuleCommunicator)
        #rule_list = [self.ruleAgreement, self.rideSharingInvolved, self.threeBookingRS]

        #
        # insert all created rules into the rule_list
        #
        rule_list = [self.ruleRideSharingInvolved]

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
