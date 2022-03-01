import os
from flask import Flask, request
from r2r_offer_utils.advanced_logger import *
import codes.incentive_provider
from codes import communicators
from codes.AL_requester import *
import json

service_name    = os.path.splitext(os.path.basename(__file__))[0]
app             = Flask(service_name)

logger = logging.getLogger(service_name)
config = ConfigLoader(LoggerFormatter(logger), service_name).config

auth_token_obt = AuthTokenObtainer()

#
# Testing examples
#
# curl -v -X GET "http://127.0.0.1:5011/?request_id=4ab9befc-5dd5-4751-96a2-d67ca18c5ad2"
# curl -v -X GET "http://127.0.0.1:5011/?request_id=53592604-d41a-42e4-8859-99e6af7e4fbe"
# curl -v -X GET "http://127.0.0.1:5011/?request_id=d6868083-354e-4b9c-87f2-15ea50934549"
#########################################################################################################################
# INCENTIVE PROVIDER INTERFACE
########################################################################################################################
@app.route('/', methods=['GET'])
def return_incentives():
    args = request.args.to_dict()
    request_id = args["request_id"]
    logger.info(f"GET request for incentives obtained with request_id = {request_id}")

    # create incentive provider
    IPM = codes.incentive_provider.IncentiveProviderManager(config, auth_token_obt)

    # execute incentive provider
    try:
        incenitve_dict = IPM.getIncentives({"request_id": request_id})
    except Exception as ex:
        incenitve_dict = None
        logger.error(f"Unexpected exception at the top level of API received: {ex} ")

    if incenitve_dict is None:
        return "Error when processing incentives", 500

    # print output on the screen (only for testing purposes)
    for key in incenitve_dict:
        for incentive in incenitve_dict[key]:
            logger.info(f"KEY={key}, incetive={incentive}, eligible={incenitve_dict[key][incentive]}")

    # write incentives to cache
    written = IPM.incentivesToCache(incenitve_dict, request_id)
    # if they could have not been written to cache, return 500
    if written:
        logger.info("Incentive data successfully written to Cache")
    else:
        return "Error writing to cache", 500
    # ?T0DO: add incentive ID to the response
    wrap_res = {
        "offers": incenitve_dict,
        "request_id": request_id
    }
    return json.dumps(wrap_res, indent=4), 200


if __name__ == '__main__':
    FLASK_PORT = config.get('flask', 'port')
    os.environ["FLASK_ENV"] = "development"
    app.run(port=int(FLASK_PORT), debug=True, use_reloader=False)
    exit(0)
########################################################################################################################
########################################################################################################################
########################################################################################################################
