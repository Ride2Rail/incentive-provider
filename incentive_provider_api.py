import os
from flask import Flask, request
from r2r_offer_utils.advanced_logger import *
import codes.incentive_provider
from codes import communicators
from codes.AL_requester import *
import json

service_name    = os.path.splitext(os.path.basename(__file__))[0]
app             = Flask(service_name)

#
# Testing examples
#
#curl -v -X GET "http://127.0.0.1:5003/incentive_provider/?request_id=97b558d0-4093-47ec-90ad-cf5903586a08"
#curl -v -X GET "http://127.0.0.1:5003/incentive_provider/?request_id=939a09ff-4e8f-40d3-9a6f-4aac0d6622f9"
#curl -v -X GET "http://127.0.0.1:5003/incentive_provider/?request_id=b6b26660-1326-4b6b-bf00-132ec7e576de"
########################################################################################################################
########################################################################################################################
########################################################################################################################
# INCENTIVE PROVIDER END-POINT
########################################################################################################################
########################################################################################################################
########################################################################################################################
@app.route('/incentive_provider/', methods=['GET'])
def return_incentives():
    args = request.args.to_dict()
    request_id = args["request_id"]
    logger.info(f"GET request for incentives obtained with request_id = {request_id}")

    # create incentive provider
    IPM     = codes.incentive_provider.IncentiveProviderManager(config)

    # execute incentive provider
    output  =  IPM.getIncentives({"request_id":request_id})

    # print output on the screen (only for testing purposes)
    if output is not None:
        for key in output:
            for incentive in output[key]:
                logger.info(f"KEY={key}, incetive={incentive}, eligible={output[key][incentive]}")
    return json.dumps(output, indent = 4), 200
########################################################################################################################
########################################################################################################################
########################################################################################################################
# TESTING END-POINTS
########################################################################################################################
########################################################################################################################
########################################################################################################################

# Requesting Agreement ledger

#
# Testing examples
#
# curl -v -X GET http://127.0.0.1:5003/ALget/22b2b69f-567c-4e62-b791-476bb0cf3825
# curl -v -X GET http://127.0.0.1:5003/ALget/d6452caf-759d-44dc-8667-0954ed879071

@app.route('/ALget/<request_id>', methods=['GET'])
def return_ALdata(request_id):
    """
    passes requests incentives
    :return: response json
    """

    logger.info(f"obtained request with id: {request_id}")

    IPM = codes.incentive_provider.IncentiveProviderManager(config)
    output = IPM.getIncentives({"request_id": request_id})

    return {"request_id": request_id, "offer_incentives": output}, 200
    #
    # if type(response) is MyResponse:
    #     logger.error("error in authentication token")
    #     return response.get_response()
    # if type(response) is dict:
    #     logger.info("json returned succesfully")
    #     return response
    # return "{}",404


# Requesting Offer-cache


#
# Testing examples
#

# curl -v -X GET http://127.0.0.1:5003/rt/d6452caf-759d-44dc-8667-0954ed879071

@app.route('/rt/<request_id>', methods=['GET'])
def redis_test(request_id):
    OCC = communicators.OfferCacheCommunicator(config)
    res = OCC.redis_request_level_item(request_id, ["traveller_id","offers", "user_id"], ["v","l","v"])
    return res, 200


if __name__ == '__main__':
    FLASK_PORT = config.get('flask', 'port')
    os.environ["FLASK_ENV"] = "development"
    app.run(port=int(FLASK_PORT), debug=True, use_reloader=False)
    exit(0)
########################################################################################################################
########################################################################################################################
########################################################################################################################
