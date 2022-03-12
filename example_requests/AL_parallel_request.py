import asyncio
import json
import time

import requests

# currently working: user1 or user2
# 4ab9befc-5dd5-4751-96a2-d67ca18c5ad2
# 53592604-d41a-42e4-8859-99e6af7e4fbe
# user_id = 'b343adc2-a2fd-4f52-9969-2cf220b46daf'
# url_get = "http://127.0.0.1:5010/" + user_id
# get_result = requests.get(url_get, data=None, headers=None)
# print(get_result.status_code)
# try:
#     print(get_result.json())
# except json.decoder.JSONDecodeError:
#     print('empty json received')

async def main():
    loop = asyncio.get_event_loop()
    url_get = "http://127.0.0.1:5011/?request_id="
    future1 = loop.run_in_executor(None, requests.get, url_get + 'example_1')
    future2 = loop.run_in_executor(None, requests.get, url_get + 'example_2')
    time.sleep(0.1)
    future3 = loop.run_in_executor(None, requests.get, url_get + 'example_3')
    response1 = await future1
    response2 = await future2
    response3 = await future3
    print(response1.json())
    print(response2.json())
    print(response3.json())

loop = asyncio.get_event_loop()
loop.run_until_complete(main())