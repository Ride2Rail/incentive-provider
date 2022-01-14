# Incentive provider

This module pre-evaluates the eligibility to receive travel incentives. The incentives 
are associated with travel offers. Current version supports the following incentives listed in the Table.

| Incentive | Description |
|:---------:|-------------|
|     10%Discount     | The incentive is associated with a travel offer if at least one ride-sharing leg is included in the travel offer.       |
|     20%Discount     | The incentive is associated with a travel offer if the travel offer contains at least one ride-sharing leg and the passenger completed at least 3 ride-shares. The counter of completed ride-shares is set to zero after allocating the incentive.  |
|      FreeSeat       | The incentive is associated with a travel offer if at least one other passenger booked at least one of the ride-shares included in the travel offer. |

## Calculation of incentives

### Incentive 10%Discount

For a given _request_id_ the corresponding list of travel offers and their and transport modes of 


### Incentive 10%Discount

### Incentive FreeSeat


# implementation

# Usage

## Local development (debug on)

## Response

# Limitations
