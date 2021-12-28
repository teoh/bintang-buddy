from config import (
    GYM_IDS,
    BEARER,
    GYM_URL_TEMPLATE,
    HEADERS
)
import optparse
import requests

parser = optparse.OptionParser()
parser.add_option('-d', '--date', dest='date',
                  help='Date (YYYYMMDD) to search courts for',
                  default="20211222")

def get_courts_from_gym(gym_id):
    resp = requests.get(GYM_URL_TEMPLATE.format(GYM_ID=gym_id),
                        headers=HEADERS)
    courts = []

    for court_info in resp.json().get('items', list()):
        courts.append((
            court_info.get('name'),
            court_info.get('resourceId')
        ))

    return courts

def get_court_schedule(court_id):
    pass
    # court_schedule_params = {
    #     "reservationId": None,
    # }

def main(date):
    print(date)
    print(HEADERS)
    gyms_to_courts = {}
    for gym, gym_id in GYM_IDS.items():
        gyms_to_courts[(gym, gym_id)] = \
            get_courts_from_gym(gym_id)
    import pdb; pdb.set_trace()

if __name__ == "__main__":
    options, args = parser.parse_args()

    date = int(options.date)
    assert date is not None, "d needs to be a date"
    main(date)

