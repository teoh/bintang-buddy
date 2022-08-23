# Will need to add to this if they ever have a new gym in the area
GYM_IDS = {
    "campbell": "17047",
    "dublin": "17100",
    "milpitas": "17043",
    "san carlos": "17099",
    "sunnyvale": "17098",
}

AUTH_URL = "https://app.bukza.com/api/client/create/16509"
GYM_URL_TEMPLATE = "https://app.bukza.com/api/resource-groups/getClientCatalog/16509/{GYM_ID}"
COURT_SCHEDULE_URL = "https://app.bukza.com/api/clientReservations/getAvailability/16509"

HEADERS = {
    "x-bukza-user-id": "16509",
    "accept": "application/json",
    "content-type": "application/json;charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
}
