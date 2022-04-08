from abc import abstractmethod, ABC
import logging

logger = logging.getLogger('incentive_provider_api.rules')


class Rule(ABC):
    def __init__(self, communicator_dict, name, incentive):
        # communicator to get required data for rule evaluation
        self.communicator_dict = communicator_dict
        self.name = name
        self.offer_dict = {}
        self.incentive = incentive


    def isFulfilled(self, data_dict):
        self.offer_dict = self.checkFulfilled(data_dict)

    @abstractmethod
    def checkFulfilled(self, data_dict):
        pass

    def wrapOCcommunication(self):
        pass

    def logOfferProblem(self, trip_offers_data):
        """
        logs the problem with offers
        :param trip_offers_data: dictionary with tripoffer data
        :return: True if there were no offers, False if a different error occured
        """
        if trip_offers_data is not None and 'output_offer_level' in trip_offers_data and \
         'offer_ids' in trip_offers_data['output_offer_level'] and not trip_offers_data['output_offer_level']['offer_ids']:
            logger.info(f"Rule: {self.name}: No offers extracted")
            # raise no offer exception
            raise NoOffersFoundException
        else:
            logger.error(f"Rule: {self.name} State: No data extracted from the Offer cache.")
            return False

########################################################################################################################
########################################################################################################################
########################################################################################################################
class TwoPassShared(Rule):
    def __init__(self, communicator_dict, incentive):
        super().__init__(communicator_dict, "TwoPassShared", incentive)

    def checkFulfilled(self, data_dict):
        # prepare request to the offer cache regarding transport modes linked to the travel offer items included in the
        communicator_data_dict = {"request_id": data_dict["request_id"],
                                  "list_offer_level_keys": [],
                                  "list_tripleg_level_keys": ["transportation_mode"]}

        logger.info(f"Rule: TwoPassShared State: About to request data from the Offer cache using: "
                    f"communicator_data_dict={communicator_data_dict}")
        # obtain data about the trip offers from the offer cache
        trip_offers_data = self.communicator_dict["offer_cache_communicator"].accessRuleData(communicator_data_dict)

        if trip_offers_data is not None and not self.communicator_dict["offer_cache_communicator"].check_empty_dict(trip_offers_data):
            # Process obtained data and evaluated id Offer items associated with the requuest are entitled to receive incentive
            tripleg_id_dict = {}
            result = {}
            try:
                for offer_id in trip_offers_data["output_offer_level"]["offer_ids"]:
                    # loop over triplegs belonging to the offer item
                    incentive = self.incentive.getIncentive()
                    for trip_leg_id in trip_offers_data["output_tripleg_level"][offer_id]["triplegs"]:
                        transportation_mode = trip_offers_data["output_tripleg_level"][offer_id][trip_leg_id]["transportation_mode"]
                        # if there is ridesharing add it to the set
                        if transportation_mode == 'others-drive-car':
                            # check if the tripleg was already checked
                            if trip_leg_id in tripleg_id_dict:
                                incentive.eligible = tripleg_id_dict[trip_leg_id]
                            else:
                                # if the tripleg was not checked check the availability for trip ID in Agreement Ledger
                                req_res = self.communicator_dict["AL_communicator"].accessRuleData({
                                    "url": "upgrSeat_url",
                                    "id": trip_leg_id
                                })
                                # if AL received proper answer
                                # add the answer to the dictionary recording checked triplegs
                                if req_res is not None:
                                    tripleg_id_dict[trip_leg_id] = req_res
                                    # if answer was true, set the incentive as checked and break the loop
                                    if req_res:
                                        incentive.eligible = True
                                        break
                    result[offer_id] = incentive
                return result

            except KeyError:
                logger.error(f"Rule: TwoPassShared: Offer cache data cannot be used to determine applicability of the incentive.")
        else:
            self.logOfferProblem(trip_offers_data)
        return {"no_offer": self.incentive}


########################################################################################################################
########################################################################################################################
########################################################################################################################
class RideSharingInvolved(Rule):

    def __init__(self, communicator_dict, incentive):
        super().__init__(communicator_dict, "RideSharingInvolved", incentive)

    def checkFulfilled(self, data_dict):

        # prepare request to the offer cache regarding transport modes linked to the travel offer items included in the
        communicator_data_dict      = {"request_id": data_dict["request_id"],
                                       "list_offer_level_keys": [],
                                       "list_tripleg_level_keys": ["transportation_mode"]}

        logger.info(f"Rule: RideSharingInvolved State: About to request data from the Offer cache using: "
                    f"communicator_data_dict={communicator_data_dict}")
        # obtain data about the trip offers from the offer cache
        trip_offers_data            = self.communicator_dict["offer_cache_communicator"].accessRuleData(communicator_data_dict)

        logger.info(f"Rule: RideSharingInvolved State: Data extracted from the Offer cache. trip_offers_data={trip_offers_data}")
        if trip_offers_data is not None and not self.communicator_dict["offer_cache_communicator"].check_empty_dict(trip_offers_data):
            # Process obtained data and evaluated id Offer items associated with the requuest are entitled to receive incentive
            # loop over travel offer items
            result = {}
            try:
                for offer_id in trip_offers_data["output_offer_level"]["offer_ids"]:
                    # loop over triplegs belonging to the offer item
                    incentive = self.incentive.getIncentive()
                    for trip_leg_id in trip_offers_data["output_tripleg_level"][offer_id]["triplegs"]:
                        transportation_mode = trip_offers_data["output_tripleg_level"][offer_id][trip_leg_id]["transportation_mode"]
                        if transportation_mode == 'others-drive-car':
                            incentive.eligible = True
                            break
                    result[offer_id]    = incentive
                return result
            except KeyError:
                logger.error(f"Rule: RideSharingInvolved State: Offer cache data cannot be used to determine applicability of the incentive.")
        else:
            self.logOfferProblem(trip_offers_data)
        return {"no_offer": self.incentive}


########################################################################################################################
########################################################################################################################
########################################################################################################################
class ThreePreviousEpisodesRS(Rule):
    # Required data: offer_id, <iterated> leg_id, traveller_id, transportation_mode
    def __init__(self, communicator_dict, incentive):
        super().__init__(communicator_dict, "ThreePreviousEpisodesRS", incentive)
        self.no_offers = False
        self.exception_state_list = \
            [ExceptionalStateHandler(404, 'message', 'Traveller does not exist', "missing user ID", False)]

    def checkFulfilled(self, data_dict):
        logger.info(f"Rule: ThreePreviousEpisodesRS State: About to request data from the Offer cache using: "
                    f"communicator_data_dict={data_dict}")
        # obtain data about the trip offers and traveller id from the offer cache
        communicator_data_dict = {"request_id": data_dict["request_id"],
                                  "offer_level_keys": ["offers", "traveller_id"],
                                  "offer_level_types": ["l", "v"]
                                  }
        user_OC_data = self.communicator_dict["offer_cache_communicator"].accessRuleData(communicator_data_dict)

        # check for ridesharing
        offer_rs_dict = self.checkRidesharing(data_dict)
        # if OC data was sucesully obtained and if there is at least one ridesharing leg
        if user_OC_data is not None and offer_rs_dict is not None:
            # if there is a any ridesharing leg
            ret_dict = {}
            if any(offer_rs_dict.values()):
                # get data from agreement ledger
                req_res = self.communicator_dict["AL_communicator"].accessRuleData({
                    "url": "disc20_url",
                    "id": user_OC_data["traveller_id"],
                    "exception_state_list": self.exception_state_list
                })
                # if there was no data obtained from AL set the result to false
                if req_res is None:
                    req_res = False
                for offer_id in offer_rs_dict.keys():
                    incentive = self.incentive.getIncentive()
                    # if there is ridesharing and the rider had
                    incentive.eligible = req_res and offer_rs_dict[offer_id]
                    # add incentive to the returned dictionary
                    ret_dict[offer_id] = incentive
            else:
                # if there are no ridesharing legs, just create the incentives
                for offer_id in offer_rs_dict.keys():
                    ret_dict[offer_id] = self.incentive.getIncentive()

            return ret_dict
        else:
            # if was no data extracted from offer cache, add it to the dictionary
            if not self.no_offers:
                logger.error(f"Rule: ThreePreviousEpisodesRS: No data extracted from the Offer cache.")
            return {"no_offer": self.incentive}

    def checkRidesharing(self, data_dict):
        communicator_data_dict = {"request_id": data_dict["request_id"],
                                  "list_offer_level_keys": [],
                                  "list_tripleg_level_keys": ["transportation_mode"]}

        logger.info(f"Rule: ThreePreviousEpisodesRS State: About to request data from the Offer cache using: "
                    f"communicator_data_dict={communicator_data_dict}")
        # obtain data about the trip offers from the offer cache
        trip_offers_data = self.communicator_dict["offer_cache_communicator"].accessRuleData(communicator_data_dict)

        logger.info(f"Rule: ThreePreviousEpisodesRS State: Data extracted from the Offer cache."
                    f" trip_offers_data={trip_offers_data}")

        if trip_offers_data is not None and not self.communicator_dict["offer_cache_communicator"].check_empty_dict(trip_offers_data):
            # Process obtained data and evaluated id Offer items associated with the requuest are entitled to receive incentive
            # loop over travel offer items
            offer_dict = {}
            try:
                for offer_id in trip_offers_data["output_offer_level"]["offer_ids"]:
                    # loop over triplegs belonging to the offer item
                    offer_dict[offer_id] = False
                    for trip_leg_id in trip_offers_data["output_tripleg_level"][offer_id]["triplegs"]:
                        transportation_mode = trip_offers_data["output_tripleg_level"][offer_id][trip_leg_id][
                            "transportation_mode"]
                        if transportation_mode == 'others-drive-car':
                            offer_dict[offer_id] = True
                            break
                return offer_dict
            except KeyError:
                logger.error(
                    f"Rule: RideSharingInvolved State: Offer cache data cannot be used to determine applicability of the incentive.")
                return None
        else:
            self.no_offers = self.logOfferProblem(trip_offers_data)
            return None


class NoOffersFoundException(Exception):
    """Raised when there are no offers in the request"""
    pass


class ExceptionalStateHandler:
    """
    Class to fluently handle exceptional states from the Agreement ledger
    """

    def __init__(self, error_code, message_key, message_value, log_message, return_value):
        self.error_code = error_code
        self.message_key = message_key
        self.message_value = message_value
        self.log_message = log_message
        self.return_value = return_value

    def is_this_state(self, error_code, response_json, url):
        if self.error_code == error_code and self.message_key in response_json and\
                self.message_value == response_json[self.message_key]:
            logger.info(f"Handled expected state in requester at url {url}: " + self.log_message)
            return True
        return False

    def return_dict(self):
        return self.return_value


class Incentive:
    """
    Class for the incentives. Main attributes are the eligibility of incentives and the superior incentive (class: Incentive).
    """
    def __init__(self, incentiveRankerID, description, incentive_above=None):
        self.incentiveRankerID = incentiveRankerID
        self.description = description
        self.eligible = False
        self.incentiveAbove = incentive_above

    def getIncentive(self):
        """
        Factory method to create an incentive
        :return: copy of the current Incentive and false eligibility
        """
        return Incentive(self.incentiveRankerID, self.description, self.incentiveAbove)
