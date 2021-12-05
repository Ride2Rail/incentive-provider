from abc import abstractmethod, ABC


class Rule(ABC):
    def __init__(self, communicator, name, key, priority_rule=None):
        self.communicator = communicator
        self.name = name
        self.key = key
        self.priorityRule = priority_rule
        self.fulfilled = None

    @abstractmethod
    def isFulfilled(self, data_dict):
        pass

    def checkFulfilled(self, data_dict, incentives):
        rule = self.communicator.accesRuleData(data_dict)
        for incentive in incentives:
            incentive.eligible = rule
        return incentives


class TwoPassShared(Rule):
    def __init__(self, communicator):
        super().__init__(communicator,
                         name="TrainSeatUpgrade",
                         key="travelEpisodeId")

    def isFulfilled(self, data_dict):
        # Required data: offer_id
        incentives = [Incentive("TrainSeatUpgrade", "Train seat upgrade")]
        # extract here all passed travelEpisodes
        pass_dict = {
            'url_suffix': self.name,
            'values': [v for k, v in data_dict if k in self.key]
        }
        return self.checkFulfilled(pass_dict, incentives)


class RideSharingInvolved(Rule):
    def isFulfilled(self, data_dict):
        # Required data: offer_id, <iterated> leg_id, transportation_mode
        incentives = [Incentive("10discount", "10% discount")]
        return self.checkFulfilled(data_dict, incentives)

    def checkFulfilled(self, data_dict, incentives):
        # 1. get all leg ids: ['<request_id>:<offer_id>:']
        # 2. iterate leg ids: [leg_id] and extract offer transportation_mode
        transport_modes = self.communicator.accesRuleData(data_dict)
        rule = 'others-drive-car' in transport_modes
        for incentive in incentives:
            incentive.eligible = rule
        return incentives


class ThreePreviousEpisodesRS(Rule):
    # Required data: offer_id, <iterated> leg_id, traveller_id, transportation_mode
    def __init__(self, communicator):
        super().__init__(communicator,
                         name="20discount",
                         key="travellerId"
                         )

    def isFulfilled(self, data_dict):
        incentives = [Incentive("20discount")]
        agr_ledg_dict = {
            'url_suffix': self.name,
            'values': data_dict[self.key]
        }
        offer_cache_dict = {
            'offer_id': data_dict['travelOfferId']
        }
        data_dict_list = {'agr_ledg_dict': agr_ledg_dict,
                          'offer_cache_dict': offer_cache_dict}
        return self.checkFulfilled(data_dict_list, incentives)

    def checkFulfilled(self, data_dict, incentives):
        # 1. get all leg ids: ['<request_id>:<offer_id>:']
        # 2. iterate leg ids: [leg_id] and extract offer transportation_mode

        agr_ledger_res = self.communicator.accesRuleData(data_dict['agr_ledg_dict'])
        transport_modes = self.communicator.accesRuleData(data_dict['offer_cache_dict'])
        rule = 'others-drive-car' in transport_modes and agr_ledger_res
        for incentive in incentives:
            incentive.eligible = rule
        return incentives

class Incentive:
    def __init__(self, incentiveRankerID, description):
        self.incentiveRankerID = incentiveRankerID
        self.description = description
        self.eligible = False
