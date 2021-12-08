import os
from flask import Flask, request
from r2r_offer_utils.advanced_logger import *
import codes.communicators
import codes.rules
import codes.incentive_provider

service_name    = os.path.splitext(os.path.basename(__file__))[0]
app             = Flask(service_name)

#
# Examples of the request
#
# curl -v -X GET "http://127.0.0.1:5003/incentive_provider/?request_id=46a4fa0d-2fd2-4317-8441-1b6a9511f1e7"
# curl -v -X GET "http://127.0.0.1:5003/incentive_provider/?request_id=696f60c1-3458-4ca9-aa96-c31ae91559a7"

########################################################################################################################
########################################################################################################################
########################################################################################################################
@app.route('/incentive_provider/', methods=['GET'])
def return_incentives():
    args = request.args.to_dict()
    request_id = args["request_id"]
    logger.info(f"GET request for incentives obtained with request_id = {request_id}")

    # test Offer cache communicator
    '''
    OCC                                         = codes.communicators.OfferCacheCommunicator()
    dict                                        = OCC.read_data_from_offer_cache(request_id,
                                                                                [],
                                                                                ["duration",
                                                                                 "cleanliness",
                                                                                 "space_available",
                                                                                 "ride_smoothness",
                                                                                 "seating_quality",
                                                                                 "internet_availability",
                                                                                 "plugs_or_charging_points",
                                                                                 "silence_area_presence",
                                                                                 "privacy_level",
                                                                                 "user_feedback",
                                                                                 "bike_on_board",
                                                                                 "likelihood_of_delays",
                                                                                 "last_minute_changes",
                                                                                 "frequency_of_service",
                                                                                 "business_area_presence"])
    '''



    '''
    OCC                                         = codes.communicators.OfferCacheCommunicator()
    dict                                        = OCC.read_data_from_offer_cache(request_id,
                                                                                  ["bookable_total", "complete_total"],
                                                                                  ["duration", "can_share_cost"])
    '''

    '''
    OCC                                         = codes.communicators.OfferCacheCommunicator()
    dict                                        = OCC.accessRuleData({"request_id":request_id,
                                                                      "list_offer_level_keys":["triplegs"],
                                                                      "list_tripleg_level_keys":[]})
    print("dict = ", dict)                                                                      
    '''

    '''
    # test rule RideSharingInvolved
    OCC         = codes.communicators.OfferCacheCommunicator()    
    RULE        = codes.rules.RideSharingInvolved({"offer_cache_communicator":OCC})
    data_dict   = {"request_id":request_id}
    RideSharing = RULE.checkFulfilled(data_dict)
    print(f"rule_output={RideSharing}")

    # show the
    if RideSharing is not None:
        for key in RideSharing:
            print(f"KEY={key}, incentive={RideSharing[key].eligible}")
    '''

    # test IncentiveProviderManager
    IPM     = codes.incentive_provider.IncentiveProviderManager()
    output  =  IPM.getIncentives({"request_id":request_id})
    # print output on the screen (only for testing purposes)
    if output is not None:
        for rule_output in output:
            for key in rule_output:
                print(f"KEY={key}, incetive={rule_output[key].incentiveRankerID}, eligible={rule_output[key].eligible}")

            #print(f"KEY={key}, incentive={output[key].eligible}")

    return "{}", 200
########################################################################################################################
########################################################################################################################
########################################################################################################################
if __name__ == '__main__':
    FLASK_PORT = config.get('flask', 'port')
    os.environ["FLASK_ENV"] = "development"
    app.run(port=int(FLASK_PORT), debug=True, use_reloader=False)
    exit(0)
########################################################################################################################
########################################################################################################################
########################################################################################################################
