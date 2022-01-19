# Incentive provider

This module pre-evaluates the eligibility to receive travel incentives. The incentives 
are associated with travel offers. Current version supports incentives listed in the following Table:

| Incentive | Description |
|:---------:|-------------|
|     10%Discount     | The incentive is associated with a travel offer item if at least one ride-sharing leg is included in any travel offer item.       |
|     20%Discount     | The incentive is associated with a travel offer item if the offer item contains at least one ride-sharing leg and the passenger completed at least 3 ride-shares. The counter of completed ride-shares is set to zero after allocating the incentive.  |
|      FreeSeat       | The incentive is associated with a travel offer item if at least one other passenger booked at least one of the ride-shares included in the travel offer item. |

## Calculation of incentives

### Incentive 10%Discount
For a given _request_id_, the corresponding list of travel offer items and the transport modes associated with 
legs are obtained from the [offer-cache](https://github.com/Ride2Rail/offer-cache).
Based on this data, the presence of ride sharing legs is analysed, in the method _checkFulfilled()_ of the class _RideSharingInvolved_ 
implemented in the script [rules.py](https://github.com/Ride2Rail/incentive-provider/blob/main/codes/rules.py).

### Incentive 20%Discount
For a given _request_id_, the corresponding list of travel offer items, Traveler ID and the transport modes associated with 
legs are obtained from the [offer-cache](https://github.com/Ride2Rail/offer-cache). 
If an offer items contains a ridesharing leg, Traveler ID is used to requested the Agreement Ledger 
module to provide infomration about the eligibility to receive 20%Discount incentive. Otherwise, it is concluded that
offer item is concluded to be not eligible for this incentive. The evaluation is implemented by 
the method checkFulfilled()_ of the class _ThreePreviousEpisodesRS_ 
implemented in the script [rules.py](https://github.com/Ride2Rail/incentive-provider/blob/main/codes/rules.py).

### Incentive FreeSeat



# Implementation

# Usage

## Local development (debug on)
The module "Incentive provider" can be launched from the terminal locally by running the script "incentive_provider_api.py":
```bash
2022-01-17 11:29:45 - incentive_provider_api - INFO - config loaded successfully
 * Serving Flask app 'incentive_provider_api' (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5003/ (Press CTRL+C to quit)
```

## Requesting Data provider service
Example of the curl command to receive a JSON file with information about the incentives associate with the travel offers included in the request which is identified by  < request_id >:
```bash
curl -X GET "http://127.0.0.1:5003/incentive_provider/?request_id=< request_id >"
```

Example of the returned JSON file:


```JSON
{
    "36e5c5b9-b434-40c4-8017-9ec79578813a": {
        "10discount": true,
        "trainSeatUpgrade": true,
        "20discount": false
    },
    "ef9012a8-918b-4e20-a724-rs1": {
        "10discount": true,
        "trainSeatUpgrade": true,
        "20discount": false
    },
    "731d2c82-e158-4d87-8cd6-df9bbcc647e6": {
        "10discount": false,
        "trainSeatUpgrade": false,
        "20discount": false
    },
    "5c08395c-7efc-4418-a2dc-c2794e7120f6": {
        "10discount": true,
        "trainSeatUpgrade": true,
        "20discount": false
    },
    "c421d948-8741-4b33-8797-3871ec8b3b7f": {
        "10discount": false,
        "trainSeatUpgrade": false,
        "20discount": false
    }
* Closing connection 0
(base)
```



## Response

# Limitations
