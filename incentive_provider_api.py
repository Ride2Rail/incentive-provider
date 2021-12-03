import os
from flask import Flask, request
from r2r_offer_utils.advanced_logger import *
import codes.communicators

service_name = os.path.splitext(os.path.basename(__file__))[0]

app = Flask(service_name)


#
# Example of the request
#
# curl -v -X GET "http://127.0.0.1:5002/incentive_provider/?request_id=76704113-6ad8-43d5-a7cc-55e48450232a"

@app.route('/incentive_provider/', methods=['GET'])
def return_incentives():
    args = request.args.to_dict()
    request_id = args["request_id"]
    logger.info(f"GET request for incentives obtained with request_id = {request_id}")

    # test communicator
    ALC = codes.communicators.OfferCacheCommunicator()

    return "{}", 200


if __name__ == '__main__':
    FLASK_PORT = my_configLoader.config.get('flask', 'port')
    os.environ["FLASK_ENV"] = "development"
    app.run(port=int(FLASK_PORT), debug=True, use_reloader=False)
    exit(0)
