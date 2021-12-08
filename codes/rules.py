from abc import abstractmethod, ABC

########################################################################################################################
########################################################################################################################
########################################################################################################################
class Rule(ABC):

    # QUESTION:
    # Why do we add name and key as class attributes (these are not used by RideSharingInvolved class)
    # would not be better to include it directly as constants only into the definition of methods that execute given rules?

    def __init__(self, communicator_dict):
        # communicator to get required data for rule evaluation
        self.communicator_list  = communicator_dict
        self.fulfilled          = None

    @abstractmethod
    def isFulfilled(self, data_dict):
        pass

    def checkFulfilled(self, data_dict):
        return None

########################################################################################################################
########################################################################################################################
########################################################################################################################
class TwoPassShared(Rule):
    def __init__(self, communicator_dict):
        super().__init__(communicator_dict)
        self.name = ""
        self.key  = ""

    def isFulfilled(self, data_dict):
        # Required data: offer_id
        incentives = [Incentive("TrainSeatUpgrade", "Train seat upgrade")]
        # extract here all passed travelEpisodes
        pass_dict = {
            'url_suffix': self.name,
            'values': [v for k, v in data_dict if k in self.key]
        }
        return self.checkFulfilled(pass_dict, incentives)
########################################################################################################################
########################################################################################################################
########################################################################################################################
class RideSharingInvolved(Rule):
    def isFulfilled(self, data_dict):
        incentive = Incentive("10discount", "10% discount")
        return self.checkFulfilled(data_dict, incentive)

    def checkFulfilled(self, data_dict, incentive):

        # prepare request to the offer cache on transport modes linked to the travel offer items included in the
        communicator_data_dict      = {"request_id": data_dict["request_id"],
                                       "list_offer_level_keys": [],
                                       "list_tripleg_level_keys": ["transportation_mode"]}

        # obtain data about the trip offers from the offer cache
        trip_offers_data            = self.communicator_dict["offer_cache_communicator"].accessRuleData(communicator_data_dict)

        # loop over travel offer items
        result = {}
        for offer_id in trip_offers_data["output_offer_level"]["offer_ids"]:
            # loop over triplegs belonging to the offer item
            incentive = Incentive("10discount", "10% discount")

            for trip_leg_id in trip_offers_data["output_tripleg_level"][offer_id]["trip_legs"]:
                transportation_mode = trip_offers_data["output_tripleg_level"][offer_id][trip_leg_id]
                if transportation_mode == 'others-drive-car':
                    incentive.eligible = True
                    break
            result[offer_id]    = incentive
        return result


'''
example of the output received from the offer cache - trip_offer_data content

dict =  {'output_offer_level': {'offer_ids': ['cb32d4fe-47fd-4b2f-aefa-01251d2fe3c6', '7e6c9839-d276-4e9a-8a30-30b3ac1557b9', '8cd79ed6-73fd-41c6-beec-60c997f675a4', 'ad124a6c-8cce-4936-a054-97a1f67c60b7', 'fa24dca4-e68a-4f66-b9ff-7a8aad78a74f', 'ae7eff45-5df0-4e7b-bd4e-ec4dc1a79d2d', 'e945ec09-f74c-42ed-8ae6-809945df54de'], 

'cb32d4fe-47fd-4b2f-aefa-01251d2fe3c6': {},
'7e6c9839-d276-4e9a-8a30-30b3ac1557b9': {}, 
'8cd79ed6-73fd-41c6-beec-60c997f675a4': {}, 
'ad124a6c-8cce-4936-a054-97a1f67c60b7': {}, 
'fa24dca4-e68a-4f66-b9ff-7a8aad78a74f': {}, 
'ae7eff45-5df0-4e7b-bd4e-ec4dc1a79d2d': {}, 
'e945ec09-f74c-42ed-8ae6-809945df54de': {}}, 

'output_tripleg_level': {
'cb32d4fe-47fd-4b2f-aefa-01251d2fe3c6': {

'triplegs': ['87cdbd26-ed09-466f-8998-283e4b180736', '71d75826-be62-4aea-9158-d25f3e69fada', '4b8936e0-b132-47a1-97c2-0b619e0d1a94', '3fd3631d-4cb4-4d0a-aaeb-804ebe7e46f8', '35895f25-8eda-451b-bcc2-f899884b5d5a'], 

'87cdbd26-ed09-466f-8998-283e4b180736': {'transportation_mode': 'walk'}, 
'71d75826-be62-4aea-9158-d25f3e69fada': {'transportation_mode': 'bus'}, 
'4b8936e0-b132-47a1-97c2-0b619e0d1a94': {'transportation_mode': 'walk'}, 
'3fd3631d-4cb4-4d0a-aaeb-804ebe7e46f8': {'transportation_mode': 'bus'}, 
'35895f25-8eda-451b-bcc2-f899884b5d5a': {'transportation_mode': 'unknown'}}, 

'7e6c9839-d276-4e9a-8a30-30b3ac1557b9': {'triplegs': ['87cdbd26-ed09-466f-8998-283e4b180736', '71d75826-be62-4aea-9158-d25f3e69fada', '4b8936e0-b132-47a1-97c2-0b619e0d1a94', '3fd3631d-4cb4-4d0a-aaeb-804ebe7e46f8', '35895f25-8eda-451b-bcc2-f899884b5d5a'], 
'87cdbd26-ed09-466f-8998-283e4b180736': {'transportation_mode': 'walk'}, 
'71d75826-be62-4aea-9158-d25f3e69fada': {'transportation_mode': 'bus'}, 
'4b8936e0-b132-47a1-97c2-0b619e0d1a94': {'transportation_mode': 'walk'}, 
'3fd3631d-4cb4-4d0a-aaeb-804ebe7e46f8': {'transportation_mode': 'bus'}, 
'35895f25-8eda-451b-bcc2-f899884b5d5a': {'transportation_mode': 'unknown'}}, 

'8cd79ed6-73fd-41c6-beec-60c997f675a4': {'triplegs': ['87cdbd26-ed09-466f-8998-283e4b180736', '71d75826-be62-4aea-9158-d25f3e69fada', '4b8936e0-b132-47a1-97c2-0b619e0d1a94', '3fd3631d-4cb4-4d0a-aaeb-804ebe7e46f8', '35895f25-8eda-451b-bcc2-f899884b5d5a'], 
'87cdbd26-ed09-466f-8998-283e4b180736': {'transportation_mode': 'walk'}, 
'71d75826-be62-4aea-9158-d25f3e69fada': {'transportation_mode': 'bus'}, 
'4b8936e0-b132-47a1-97c2-0b619e0d1a94': {'transportation_mode': 'walk'}, 
'3fd3631d-4cb4-4d0a-aaeb-804ebe7e46f8': {'transportation_mode': 'bus'}, 
'35895f25-8eda-451b-bcc2-f899884b5d5a': {'transportation_mode': 'unknown'}}, 

'ad124a6c-8cce-4936-a054-97a1f67c60b7': {'triplegs': ['0740ca13-e40b-4500-9329-d44cfd642376', 'd0eb8407-dc8f-4d27-930f-f792030ca8e1', '3fea060e-0dc8-4705-aabb-8e960c644f90'], 
'0740ca13-e40b-4500-9329-d44cfd642376': {'transportation_mode': 'bus'}, 
'd0eb8407-dc8f-4d27-930f-f792030ca8e1': {'transportation_mode': 'bus'}, 
'3fea060e-0dc8-4705-aabb-8e960c644f90': {'transportation_mode': 'cycle'}}, 

'fa24dca4-e68a-4f66-b9ff-7a8aad78a74f': {'triplegs': ['0740ca13-e40b-4500-9329-d44cfd642376', 'd0eb8407-dc8f-4d27-930f-f792030ca8e1', '3fea060e-0dc8-4705-aabb-8e960c644f90'], 
'0740ca13-e40b-4500-9329-d44cfd642376': {'transportation_mode': 'bus'}, 
'd0eb8407-dc8f-4d27-930f-f792030ca8e1': {'transportation_mode': 'bus'}, 
'3fea060e-0dc8-4705-aabb-8e960c644f90': {'transportation_mode': 'cycle'}}, 

'ae7eff45-5df0-4e7b-bd4e-ec4dc1a79d2d': {'triplegs': ['0740ca13-e40b-4500-9329-d44cfd642376', 'd0eb8407-dc8f-4d27-930f-f792030ca8e1', '3fea060e-0dc8-4705-aabb-8e960c644f90'], 
'0740ca13-e40b-4500-9329-d44cfd642376': {'transportation_mode': 'bus'}, 
'd0eb8407-dc8f-4d27-930f-f792030ca8e1': {'transportation_mode': 'bus'}, 
'3fea060e-0dc8-4705-aabb-8e960c644f90': {'transportation_mode': 'cycle'}}, 

'e945ec09-f74c-42ed-8ae6-809945df54de': {'triplegs': ['f7b6d950-dd89-48fd-becc-33d93be8ac77', '96065b79-3d6f-4bd5-ba29-6692b1860926', 'a031c77f-ebd8-44ff-a772-997f62976219'], 
'f7b6d950-dd89-48fd-becc-33d93be8ac77': {'transportation_mode': 'cycle'}, 
'96065b79-3d6f-4bd5-ba29-6692b1860926': {'transportation_mode': 'unknown'}, 
'a031c77f-ebd8-44ff-a772-997f62976219': {'transportation_mode': 'unknown'}}}}
'''



########################################################################################################################
########################################################################################################################
########################################################################################################################
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
########################################################################################################################
########################################################################################################################
########################################################################################################################
class Incentive:
    def __init__(self, incentiveRankerID, description):
        self.incentiveRankerID = incentiveRankerID
        self.description = description
        self.eligible = False
