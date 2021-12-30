import os
# Will need to add to this if they ever have a new gym in the area
GYM_IDS = {
    "campbell": "17047",
    "dublin": "17100",
    "milpitas": "17043",
    "san carlos": "17099",
    "sunnyvale": "17098"
}

# LOL I'm sure this is safe... right??
BEARER = os.getenv('BEARER', None)
assert BEARER, "Did you set the BEARER env variable? See https://github.com/teoh/bintang-buddy/blob/main/README.md#getting-the-bearer-token"

GYM_URL_TEMPLATE = "https://app.bukza.com/api/resource-groups/getClientCatalog/16509/{GYM_ID}"
COURT_SCHEDULE_URL = "https://app.bukza.com/api/clientReservations/getAvailability/16509"

HEADERS = {
    "x-bukza-user-id": "16509",
    "authorization": "Bearer {}".format(BEARER),
    "accept": "application/json",
    "content-type": "application/json;charset=UTF-8",
    "x-requested-with": "XMLHttpRequest"
}
