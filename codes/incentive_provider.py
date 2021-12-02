from rules import *
from communicators import *


class Incentive:
    def __init__(self, description):
        self.eligible = False
        self.description = description


class IncentiveProvider:
    def __init__(self, ruleList):
        self.ruleList = ruleList

    def getEligibleIncentives(self, data_dict):
        return [rule.isFullfilled(data_dict) for rule in self.ruleList]

    def consistencyCheck(self):
        pass


class IncentiveProviderManager:
    def __init__(self):
        self.ruleAgreement = TwoPassShared(OfferCacheCommunicator())
        self.agreementRuleCommunicator = AgreementLedgerCommunicator()
        self.rideSharingInvolved = RideSharingInvolved(self.agreementRuleCommunicator)
        self.threeBookingRS = ThreePreviousEpisodesRS(self.agreementRuleCommunicator)

        rule_list = [self.ruleAgreement, self.rideSharingInvolved, self.threeBookingRS]
        self.incentiveProvider = IncentiveProvider(rule_list)

    def getIncentives(self, data_dict):
        allIncentives = self.incentiveProvider.getEligibleIncentives(data_dict)
        return self.incentiveProvider.consistencyCheck(allIncentives)


class TravelOfferIterator:
    def __init__(self):
        pass
