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

# add two bookings with RS of the users user0 and user2 - subset_5
# traveller_id: bb36cb92-0e8c-489e-bb20-ea93b50e5490, bookingId: book-1-user0, travelEpisodeId: bd29a292-26c0-4768-9c94-rs1,  start, end events
# traveller_id: 58ac96c2-df24-4429-872d-b8b1a0328235, bookingId: book-1-user2, travelEpisodeId: bd29a292-26c0-4768-9c94-rs1 start, end events

user_0_1_dic = booking_post_dict.copy()

user_0_1_dic['id'] = 'book-1-user0'
user_0_1_dic['travellerId'] = 'bb36cb92-0e8c-489e-bb20-ea93b50e5490'
user_0_1_dic['travelEpisodeId'] = 'bd29a292-26c0-4768-9c94-rs1'
user_0_1_dic['lyftId'] = 'lyft-1-user0'
user_0_1_dic['driverId'] = 'driver-1-user0'

post_res = send_request_AL(user_0_1_dic, "booking")
print(post_res.status_code)

event_start_dict = {
        "id": f'ev-{user_0_1_dic["id"]}-start',
        "driverId": user_0_1_dic["driverId"],
        "type": "start",
        "bookingId": user_0_1_dic["id"],
        "travellerId": user_0_1_dic["travellerId"],
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



user_2_1_dic = booking_post_dict.copy()

user_2_1_dic['id'] = 'book-1-user2'
user_2_1_dic['travellerId'] = '58ac96c2-df24-4429-872d-b8b1a0328235'
user_2_1_dic['travelEpisodeId'] = 'bd29a292-26c0-4768-9c94-rs1'
user_2_1_dic['lyftId'] = 'lyft-1-user2'
user_2_1_dic['driverId'] = 'driver-1-user2'

post_res = send_request_AL(user_2_1_dic, "booking")
print(post_res.status_code)

event_start_dict = {
        "id": f'ev-{user_2_1_dic["id"]}-start',
        "driverId": user_2_1_dic["driverId"],
        "type": "start",
        "bookingId": user_2_1_dic["id"],
        "travellerId": user_2_1_dic["travellerId"],
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


# subset_4_no_5_tsp_075_rs2.xml
# traveller_id: bb36cb92-0e8c-489e-bb20-ea93b50e5490, booking_id: book-2-user0, travelEpisodeId: bd29a292-26c0-4768-9c94-rs2, no events
# traveller_id: 58ac96c2-df24-4429-872d-b8b1a0328235, booking_id: book-2-user2, travelEpisodeId: bd29a292-26c0-4768-9c94-rs2, no events


user_0_2_dic = booking_post_dict.copy()

user_0_2_dic['id'] = 'book-2-user0'
user_0_2_dic['travellerId'] = 'bb36cb92-0e8c-489e-bb20-ea93b50e5490'
user_0_2_dic['travelEpisodeId'] = 'bd29a292-26c0-4768-9c94-rs2'
user_0_2_dic['lyftId'] = 'lyft-2-user0'
user_0_2_dic['driverId'] = 'driver-2-user0'


user_2_2_dic = booking_post_dict.copy()

user_2_2_dic['id'] = 'book-2-user2'
user_2_2_dic['travellerId'] = '58ac96c2-df24-4429-872d-b8b1a0328235'
user_2_2_dic['travelEpisodeId'] = 'bd29a292-26c0-4768-9c94-rs2'
user_2_2_dic['lyftId'] = 'lyft-2-user2'
user_2_2_dic['driverId'] = 'driver-2-user2'

post_res = send_request_AL(user_0_2_dic, "booking")
print(post_res.status_code)

post_res2 = send_request_AL(user_2_2_dic, "booking")
print(post_res2.status_code)

# add a single booking for user1 - subset_4_no_9_tsp_075.xml
# this should have no eligibility
# traveller_id: 9d2191ed-ba28-45d0-a0a8-f5dc4ad9e0f5, booking_id: book-2-user1, travelEpisode: 9465a4c7-8867-4ce2-834e-rs9, start and end events

user_1_1_dic = booking_post_dict.copy()

user_1_1_dic['id'] = 'book-2-user1'
user_1_1_dic['travellerId'] = '9d2191ed-ba28-45d0-a0a8-f5dc4ad9e0f5'
user_1_1_dic['travelEpisodeId'] = '9465a4c7-8867-4ce2-834e-rs91'
user_1_1_dic['lyftId'] = 'lyft-2-user1'
user_1_1_dic['driverId'] = 'driver-2-user1'

post_res = send_request_AL(user_1_1_dic, "booking")
print(post_res.status_code)

event_start_dict = {
        "id": f'ev-{user_1_1_dic["id"]}-start',
        "driverId": user_1_1_dic["driverId"],
        "type": "start",
        "bookingId": user_1_1_dic["id"],
        "travellerId": user_1_1_dic["travellerId"],
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