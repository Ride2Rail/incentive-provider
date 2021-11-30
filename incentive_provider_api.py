import os
from flask import Flask, request
from r2r_omr_utils.advanced_logger import *


service_name = os.path.splitext(os.path.basename(__file__))[0]

app = Flask(service_name)

#
# Example of the request
#
# curl -v -X GET "http://127.0.0.1:5002/incentive_provider/?user_id=2c62daac-815c-4ca6-8eef-9e160affa279&travel_offer_id=25d5f8"

@app.route('/incentive_provider/', methods=['GET'])
def return_incentives():
    args                = request.args.to_dict()
    user_id             = args["user_id"]
    travel_offer_id     = args["travel_offer_id"]
    logger.info(f"GET request for incentives obtained with user_id ={user_id}, travel_offer_ID={travel_offer_id}".format(user_id=user_id, travel_offer_id=travel_offer_id))

    return "{}", 200





if __name__ == '__main__':
    FLASK_PORT = my_configLoader.config.get('cache', 'port')
    os.environ["FLASK_ENV"] = "development"
    app.run(port=int(FLASK_PORT), debug=True, use_reloader=False)
    exit(0)