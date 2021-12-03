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

    def isFulfilledInc(self, data_dict, incentive_names):
        incentives = [Incentive(inc_name) for inc_name in incentive_names]
        # if the priority rule is not fulfilled
        if self.priorityRule is not None and self.priorityRule.fulfilled:
            for incentive in incentives:
                incentive.eligible = False
            return incentives
        return self.checkFulfilled(data_dict, incentives)

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
        incentives = [Incentive("TrainSeatUpgrade")]
        # extract here all passed travelEpisodes
        pass_dict = {
            'url_suffix': self.name,
            'values': [v for k, v in data_dict if k in self.key]
        }
        return self.checkFulfilled(pass_dict, incentives)


class RideSharingInvolved(Rule):
    def isFulfilled(self, data_dict):
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
    def __init__(self, communicator):
        super().__init__(communicator,
                         name="20discount",
                         key="travellerId"
                         )

    def isFulfilled(self, data_dict):
        incentives = [Incentive("20discount")]
        pass_dict = {
            'url_suffix': self.name,
            'values': data_dict[self.key]
        }
        return self.checkFulfilled(pass_dict, incentives)


class Incentive:
    def __init__(self, incentiveRankerID, description):
        self.incentiveRankerID = incentiveRankerID
        self.eligible = False
        self.description = description