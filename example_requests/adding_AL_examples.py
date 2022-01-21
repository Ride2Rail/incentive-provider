import json
import requests

url = "https://ledger.r2r.inlecom.eu/api/v1/token"
headers = {'Authorization': 'Basic aW5jZW50aXZlOk16OWVuUmph',
           'accept': 'application/json'}

token_req = requests.post(url, headers=headers)
print('Token request code: ' + token_req.status_code.__str__())
auth_token = token_req.json()['access_token']


def add_rs_example(auth_token, lyftId, driverId, travelEpisodeId, travellerId, bookingId, eventId1, eventId2):
    res_code_list = []
    req_dict = {
        "lyftId": lyftId,
        "driverId": driverId,
        "travelExpertId": "ride2rail, ip4",
        "price": 1.208282,
        "travelEpisodeId": travelEpisodeId,
        "travellerId": travellerId,
        "currency": "ISO4217",
        "id": bookingId,
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

    url_post = "https://ledger.r2r.inlecom.eu/api/v1/booking"
    get_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    post_result = requests.post(url_post, data=json.dumps(req_dict), headers=get_headers)
    res_code_list.append(post_result.status_code)

    event_dict1 = {
        "id": eventId1,
        "driverId": driverId,
        "type": "start",
        "bookingId": bookingId,
        "travellerId": travelEpisodeId,
    }

    event_dict2 = {
        "id": eventId2,
        "driverId": driverId,
        "subtype": "driver cancels, passenger doesn't show up",
        "description": "He just didnt show up",
        "travellerId": travelEpisodeId,
        "type": "end",
        "bookingId": bookingId
    }

    for event in [event_dict1, event_dict2]:
        url_post = "https://ledger.r2r.inlecom.eu/api/v1/event/"
        post_result = requests.post(url_post, data=json.dumps(event), headers=get_headers)
        res_code_list.append(post_result.status_code)
    return res_code_list

add_rs_example(auth_token, "lift-2", "driver-2", "ef9012a8-918b-4e20-a724-rs2", "b343adc2-a2fd-4f52-9969-2cf220b46daf",
               "book_id_2", "event-5", "event-6")

add_rs_example(auth_token, "lift-3", "driver-3", "ef9012a8-918b-4e20-a724-rs3", "b343adc2-a2fd-4f52-9969-2cf220b46daf",
               "book-id-3", "event-7", "event-8")

add_rs_example(auth_token, "lift-4", "driver-4", "ef9012a8-918b-4e20-a724-rs4", "b343adc2-a2fd-4f52-9969-2cf220b46daf",
               "book-id-4", "event-9", "event-10")

add_rs_example(auth_token, "lift-5", "driver-5", "ef9012a8-918b-4e20-a724-rs5", "b343adc2-a2fd-4f52-9969-2cf220b46daf",
               "book-id-5", "event-11", "event-12")

add_rs_example(auth_token, "lift-6", "driver-6", "ef9012a8-918b-4e20-a724-rs6", "b343adc2-a2fd-4f52-9969-2cf220b46daf",
               "book-id-6", "event-13", "event-14")

url_get = "https://ledger.r2r.inlecom.eu/api/v1/incentive/20discount/b343adc2-a2fd-4f52-9969-2cf220b46daf"
get_headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + auth_token}
get_result = requests.get(url_get, headers=get_headers)
get_result.json()

url_get = "https://ledger.r2r.inlecom.eu/api/v1/incentive/upgradeSeat/4d8495db-02d5-4a21-b1a9-rs1"
get_headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + auth_token}
get_result = requests.get(url_get, headers=get_headers)
get_result.json()