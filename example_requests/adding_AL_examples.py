import json
import requests

"""
The dictionary to add a leg
"""

url = "https://ledger.r2r.inlecom.eu/api/v1/token"
headers = {'Authorization': 'Basic aW5jZW50aXZlOk16OWVuUmph',
           'accept': 'application/json'}

token_req = requests.post(url, headers=headers)
print('Token request code: ' + token_req.status_code.__str__())
auth_token = token_req.json()['access_token']

def send_request_AL(data_dict, url_suffix):
    url_post = f"https://ledger.r2r.inlecom.eu/api/v1/{url_suffix}"
    get_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    post_result = requests.post(url_post, data=json.dumps(data_dict), headers=get_headers)
    return post_result

def post_booking(id, travellerId, travelEpisodeId, lyftId, driverId):
    user_dic = booking_post_dict.copy()
    user_dic['id'] = id
    user_dic['travellerId'] = travellerId
    user_dic['travelEpisodeId'] = travelEpisodeId
    user_dic['lyftId'] = lyftId
    user_dic['driverId'] = driverId
    post_res = send_request_AL(user_dic, "booking")
    print(f'Booking request code: {post_res.status_code}')
    return user_dic

def post_events(user_dic):
    event_start_dict = {
        "id": f'ev-{user_dic["id"]}-start',
        "driverId": user_dic["driverId"],
        "type": "start",
        "bookingId": user_dic["id"],
        "travellerId": user_dic["travellerId"],
    }

    event_end_dict = event_start_dict.copy()
    event_end_dict.update({'id': f'ev-{event_start_dict["id"]}-end',
                           'subtype': "driver cancels, passenger doesn't show up",
                           'description': "He just didn't show up",
                           "type": "end"})

    post_res = send_request_AL(event_start_dict, "event/")
    print(f'Start request code: {post_res.status_code}')
    post_res2 = send_request_AL(event_end_dict, "event/")
    print(f'End request code: {post_res2.status_code}')

booking_post_dict = {
    "lyftId": "",
    "driverId": "",
    "travelExpertId": "ride2rail, ip4",
    "price": 1.208282,
    "travelEpisodeId": "",
    "travellerId": "",
    "currency": "ISO4217",
    "id": "",
    "inventory": [
        {
            "quantity": 2,
            "consumable": "seats"
        },
        {
            "quantity": 2,
            "consumable": "seats"
        }
    ],
    "status": "placed"
}


def check_travelEpisode(travel_episode_id, auth_token):
    """
    Checks if the given travel episode exists
    :param travel_episode_id: id of the travel episode
    :param auth_token: authentication token 
    :return: 1 if the episode exists, 0 if it does not exist, -1 if there was an error
    """
    url_get = f"https://ledger.r2r.inlecom.eu/api/v1/incentive/upgradeSeat/{travel_episode_id}"
    get_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    get_result = requests.get(url_get, headers=get_headers)
    try:
        if get_result.status_code == 200:
            if 'check' in get_result.json():
                return 1
        elif get_result.status_code == 404 and 'message' in get_result.json():
            return 0
    except Exception as e:
        print(f"Exception when obtaining travel episode: {e}")
    return -1


def get_booking(booking_id, auth_token):
    url_get = f"https://ledger.r2r.inlecom.eu/api/v1/booking/{booking_id}"
    get_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    get_result = requests.get(url_get, headers=get_headers)
    try:
        if get_result.status_code == 200:
            return get_result.json()
    except Exception as e:
        print(f"Exception when obtaining booking episode: {e}")
    return 'booking does not exist'


def check_booking(booking_id, auth_token):
    url_get = f"https://ledger.r2r.inlecom.eu/api/v1/booking/{booking_id}"
    get_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    get_result = requests.get(url_get, headers=get_headers)
    try:
        if get_result.status_code == 200:
            return 1
        elif get_result.status_code == 404 and 'message' in get_result.json():
            return 0
    except Exception as e:
        print(f"Exception when obtaining booking episode: {e}")
    return -1

# add two bookings with RS of the users user0 and user2 - subset_5
# traveller_id: bb36cb92-0e8c-489e-bb20-ea93b50e5490, bookingId: book-1-user0, travelEpisodeId: bd29a292-26c0-4768-9c94-rs1, start, end events
# traveller_id: 58ac96c2-df24-4429-872d-b8b1a0328235, bookingId: book-1-user2, travelEpisodeId: bd29a292-26c0-4768-9c94-rs1, start, end events


# if check_travelEpisode('bd29a292-26c0-4768-9c94-rs1', auth_token) == 0:
#     user0_1_dic = post_booking(id='book-1-user0', travellerId='bb36cb92-0e8c-489e-bb20-ea93b50e5490',
#                                travelEpisodeId='bd29a292-26c0-4768-9c94-rs1', lyftId='lyft-1-user0',
#                                driverId='driver-1-user0')
#     post_events(user0_1_dic)
#
# user0_1_dic = post_booking(id='book-1-user2', travellerId='58ac96c2-df24-4429-872d-b8b1a0328235',
#              travelEpisodeId='bd29a292-26c0-4768-9c94-rs1', lyftId='lyft-1-user2', driverId='driver-1-user2')
#
# post_events(user0_1_dic)

# subset_4_no_5_tsp_075_rs2.xml
# traveller_id: bb36cb92-0e8c-489e-bb20-ea93b50e5490, booking_id: book-2-user0, travelEpisodeId: bd29a292-26c0-4768-9c94-rs2, no events
# traveller_id: 58ac96c2-df24-4429-872d-b8b1a0328235, booking_id: book-2-user2, travelEpisodeId: bd29a292-26c0-4768-9c94-rs2, no events

# check_travelEpisode('bd29a292-26c0-4768-9c94-rs2', auth_token)
#
# user0_2_dic = post_booking(id='book-2-user0', travellerId='bb36cb92-0e8c-489e-bb20-ea93b50e5490',
#              travelEpisodeId='bd29a292-26c0-4768-9c94-rs2', lyftId='lyft-1-user0', driverId='driver-2-user0')
#
# # post_events(user0_1_dic)
#
# user2_2_dic = post_booking(id='book-2-user2', travellerId='58ac96c2-df24-4429-872d-b8b1a0328235',
#              travelEpisodeId='bd29a292-26c0-4768-9c94-rs2', lyftId='lyft-2-user2', driverId='driver-2-user0')


# add a single booking for user1 - subset_4_no_9_tsp_075.xml
# this should have no eligibility
# traveller_id: 9d2191ed-ba28-45d0-a0a8-f5dc4ad9e0f5, booking_id: book-2-user1, travelEpisode: 9465a4c7-8867-4ce2-834e-rs9, start and end events

# user1_1_dic = post_booking(id='book-2-user1', travellerId='9d2191ed-ba28-45d0-a0a8-f5dc4ad9e0f5',
#              travelEpisodeId='9465a4c7-8867-4ce2-834e-rs3', lyftId='lyft-1-user1', driverId='driver-1-user1')
#
# post_events(user0_1_dic)

###
# Test case 1, demo-user, subset_4_no_9_tsp_025_v2.xml
# Add 2, if not eligible ten 3 trips for this user
# b343adc2-a2fd-4f52-9969-2cf220b46daf, 4d8495db-02d5-4a21-b1a9-rs1

if check_travelEpisode('4d8495db-02d5-4a21-b1a9-rs1', auth_token) == 0:
    demouser_1_dic = post_booking(id='book-1-demouser', travellerId='3425fc34-7f1c-4b04-90d3-7a3966eeaa4e',
                                 travelEpisodeId='4d8495db-02d5-4a21-b1a9-rs1', lyftId='lyft-1-demouser', driverId='driver-1-demouser')
    post_events(demouser_1_dic)


    demouser_2_dic = booking_post_dict.copy()

    demouser_2_dic['id'] = 'book-2-demouser'
    demouser_2_dic['travellerId'] = '3425fc34-7f1c-4b04-90d3-7a3966eeaa4e'
    demouser_2_dic['travelEpisodeId'] = '4d8495db-02d5-4a21-b1a9-rs12'
    demouser_2_dic['lyftId'] = 'lyft-2-demouser'
    demouser_2_dic['driverId'] = 'driver-1-demouser'

    event_start_dict = {
            "id": f'ev-{demouser_2_dic["id"]}-start',
            "driverId": demouser_2_dic["driverId"],
            "type": "start",
            "bookingId": demouser_2_dic["id"],
            "travellerId": demouser_2_dic["travellerId"],
        }

    event_end_dict = event_start_dict.copy()
    event_end_dict.update({'id': f'ev-{event_start_dict["id"]}-end',
                           'subtype': "driver cancels, passenger doesn't show up",
                           'description': "He just didn't show up",
                           "type": "end"})

    post_res = send_request_AL(event_start_dict, "event/")
    print(post_res.status_code)
    post_res2 = send_request_AL(event_end_dict, "event/")
    print(post_res2.status_code)

    demouser_3_dic = booking_post_dict.copy()

    demouser_3_dic['id'] = 'book-3-demouser'
    demouser_3_dic['travellerId'] = '3425fc34-7f1c-4b04-90d3-7a3966eeaa4e'
    demouser_3_dic['travelEpisodeId'] = '4d8495db-02d5-4a21-b1a9-rs13'
    demouser_3_dic['lyftId'] = 'lyft-3-demouser'
    demouser_3_dic['driverId'] = 'driver-1-demouser'

    post_events(demouser_3_dic)

    demouser_dic = booking_post_dict.copy()

    demouser_dic['id'] = 'book-4-demouser'
    demouser_dic['travellerId'] = '3425fc34-7f1c-4b04-90d3-7a3966eeaa4e'
    demouser_dic['travelEpisodeId'] = '4d8495db-02d5-4a21-b1a9-rs1'
    demouser_dic['lyftId'] = 'lyft-4-demouser'
    demouser_dic['driverId'] = 'driver-1-demouser'

    post_res = send_request_AL(demouser_dic, "booking")
    print(post_res.status_code)

###
# Test case 2, user 10,
# 3425fc34-7f1c-4b04-90d3-7a3966eeaa4e, 4d8495db-02d5-4a21-b1a9-rs1

if check_travelEpisode('4d8495db-02d5-4a21-b1a9-rs1', auth_token) == 0:
    post_booking(id='book-1-user10', travellerId='b343adc2-a2fd-4f52-9969-2cf220b46daf',
                 travelEpisodeId='4d8495db-02d5-4a21-b1a9-rs1', lyftId='lyft-1-user10', driverId='driver-1-demouser')
######
# Test case 5
# user3, e0d4fbc7-0015-4c2f-8f07-2d8945a17d68
# 9465a4c7-8867-4ce2-834e-rs1
# in request responses to 20% discount the traveller does not exist

# add another booking for this leg to get 10 eligibility
if check_travelEpisode('9465a4c7-8867-4ce2-834e-rs1', auth_token) == 0:
    # add booking for an alternative user so there are more users
    user3alt_dic = post_booking(id='book-1-user3alt', travellerId='e0d4fbc7-0015-4c2f-8f07-user3alt',
                 travelEpisodeId='9465a4c7-8867-4ce2-834e-rs1', lyftId='lyft-1-user3', driverId='driver-1-user3')

    user3_dic = post_booking(id='book-1-user3', travellerId='e0d4fbc7-0015-4c2f-8f07-2d8945a17d68',
                 travelEpisodeId='9465a4c7-8867-4ce2-834e-rs1', lyftId='lyft-1-user3', driverId='driver-1-user3')


######
# Test case 6
# Add 3 completed trips for this user
# 03d19a6c-8789-44a3-9bb9-a32c253230c0
# 9465a4c7-8867-4ce2-834e-rs2

#
if check_booking("book-1-user4", auth_token) == 0:
    user4_1_dic = post_booking(id='book-1-user4', travellerId='03d19a6c-8789-44a3-9bb9-a32c253230c0',
                 travelEpisodeId='9465a4c7-8867-4ce2-834e-rs21', lyftId='lyft-1-user4', driverId='driver-1-user4')

    post_events(user4_1_dic)
    #
    user4_2_dic = post_booking(id='book-2-user4', travellerId='03d19a6c-8789-44a3-9bb9-a32c253230c0',
                 travelEpisodeId='9465a4c7-8867-4ce2-834e-rs22', lyftId='lyft-2-user4', driverId='driver-1-user4')

    post_events(user4_2_dic)
    #
    user4_3_dic = post_booking(id='book-3-user4', travellerId='03d19a6c-8789-44a3-9bb9-a32c253230c0',
                 travelEpisodeId='9465a4c7-8867-4ce2-834e-rs23', lyftId='lyft-3-user4', driverId='driver-1-user4')

    post_events(user4_3_dic)

    user4_4_dic = post_booking(id='book-4-user4', travellerId='03d19a6c-8789-44a3-9bb9-a32c253230c0',
                 travelEpisodeId='9465a4c7-8867-4ce2-834e-rs2', lyftId='lyft-4-user4', driverId='driver-1-user4')
