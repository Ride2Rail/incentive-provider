import json
import requests

url = "https://ledger.r2r.inlecom.eu/api/v1/token"
headers = {'Authorization': 'Basic aW5jZW50aXZlOk16OWVuUmph',
           'accept': 'application/json'}

token_req = requests.post(url, headers=headers)
print('Token request code: ' + token_req.status_code.__str__())
auth_token = token_req.json()['access_token']

url_get = "https://ledger.r2r.inlecom.eu/api/v1/incentive/20discount/26e75a9e-cc02-4414-abf9-ac06a17df474-v-1"
get_headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + auth_token}
get_result = requests.get(url_get, headers=get_headers)
print(get_result.content)

url_get = "https://ledger.r2r.inlecom.eu/api/v1/incentive/upgradeSeat/4d8495db-02d5-4a21-b1a9-rs1"
get_headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + auth_token}
get_result = requests.get(url_get, headers=get_headers)
print(get_result.content)
