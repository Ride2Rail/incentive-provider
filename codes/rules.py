from abc import abstractmethod, ABC


class Rule(ABC):
    def __init__(self, rule_checker, name, key, priority_rule = None):
        self.ruleChecker = rule_checker
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
        rule = self.ruleChecker.checkRule(data_dict)
        for incentive in incentives:
            incentive.eligible = rule
        return incentives


class TwoPassShared(Rule):
    def __init__(self, rule_checker):
        super().__init__(rule_checker,
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
        incentives = [Incentive("10discount")]
        return self.checkFulfilled(data_dict, incentives)

    def checkFulfilled(self, data_dict, incentives):
        rule = 'others-drive-car' in data_dict['TransportModes']
        for incentive in incentives:
            incentive.eligible = rule
        return incentives


class ThreePreviousEpisodesRS(Rule):
    def __init__(self, rule_checker):
        super().__init__(rule_checker,
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
