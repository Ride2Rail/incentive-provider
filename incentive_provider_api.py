import os
from flask import Flask, request
from r2r_offer_utils.advanced_logger import *
import codes.communicators

service_name = os.path.splitext(os.path.basename(__file__))[0]

app = Flask(service_name)


#
# Example of the request
#
# curl -v -X GET "http://127.0.0.1:5003/incentive_provider/?request_id=46a4fa0d-2fd2-4317-8441-1b6a9511f1e7"

########################################################################################################################
########################################################################################################################
########################################################################################################################
@app.route('/incentive_provider/', methods=['GET'])
def return_incentives():
    args = request.args.to_dict()
    request_id = args["request_id"]
    logger.info(f"GET request for incentives obtained with request_id = {request_id}")

    # test communicator
    ALC                                         = codes.communicators.OfferCacheCommunicator()

    dict                                        = ALC.read_data_from_offer_cache(request_id,
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
    dict                                        = ALC.read_data_from_offer_cache(request_id,
                                                                                  ["bookable_total", "complete_total"],
                                                                                  ["duration", "can_share_cost"])
    '''


    print("dict = ", dict)
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
