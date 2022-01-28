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
        "travellerId": travellerId,
    }

    event_dict2 = {
        "id": eventId2,
        "driverId": driverId,
        "subtype": "driver cancels, passenger doesn't show up",
        "description": "He just didnt show up",
        "travellerId": travellerId,
        "type": "end",
        "bookingId": bookingId
    }

    for event in [event_dict1, event_dict2]:
        url_post = "https://ledger.r2r.inlecom.eu/api/v1/event/"
        post_result = requests.post(url_post, data=json.dumps(event), headers=get_headers)
        res_code_list.append(post_result.status_code)
    return res_code_list

add_rs_example(auth_token=auth_token, lyftId="lift-10", driverId="driver-2",
               travelEpisodeId="ef9012a8-918b-4e20-a724-rs10", travellerId="b343adc2-a2fd-4f52-9969-2cf220b46daf",
               bookingId="book-id-10", eventId1="event-15", eventId2="event-16")

add_rs_example(auth_token=auth_token, lyftId="lift-11", driverId="driver-3", travelEpisodeId="ef9012a8-918b-4e20-a724-rs11", travellerId="b343adc2-a2fd-4f52-9969-2cf220b46daf",
               bookingId="book-id-11", eventId1="event-17", eventId2="event-18")

add_rs_example(auth_token, "lift-12", "driver-4", "ef9012a8-918b-4e20-a724-rs12", "b343adc2-a2fd-4f52-9969-2cf220b46daf",
               "book-id-12", "event-19", eventId2="event-20")

result5 = add_rs_example(auth_token, "lift-13", "driver-5", "ef9012a8-918b-4e20-a724-rs13", "b343adc2-a2fd-4f52-9969-2cf220b46dad",
               "book-id-13", "event-21", eventId2="event-22")

result6 = add_rs_example(auth_token, "lift-14", "driver-6", "ef9012a8-918b-4e20-a724-rs14", "b343adc2-a2fd-4f52-9969-2cf220b46dad",
               "book-id-14", "event-23", "event-24")

result7 = add_rs_example(auth_token, "lift-14", "driver-6", "ef9012a8-918b-4e20-a724-rs15", "b343adc2-a2fd-4f52-9969-2cf220b46dag",
               "book-id-15", "event-25", "event-26")

result8 = add_rs_example(auth_token, "lift-15", "driver-7", "episode-1", "traveller-1",
               "book-id-16", "event-27", "event-28")

result9 = add_rs_example(auth_token, "lift-15", "driver-7", "episode-2", "traveller-2",
               "book-id-17", "event-31", "event-32")


url_get = "https://ledger.r2r.inlecom.eu/api/v1/incentive/20discount/b343adc2-a2fd-4f52-9969-2cf220b46dad"
get_headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + auth_token}
get_result = requests.get(url_get, headers=get_headers)
print(get_result.json())

url_get = "https://ledger.r2r.inlecom.eu/api/v1/incentive/upgradeSeat/ef9012a8-918b-4e20-a724-rs15"
get_headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + auth_token}
get_result = requests.get(url_get, headers=get_headers)
print(get_result.json())