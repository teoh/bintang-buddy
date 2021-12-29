from config import (
    GYM_IDS,
    BEARER,
    GYM_URL_TEMPLATE,
    COURT_SCHEDULE_URL,
    HEADERS
)
from datetime import datetime, timedelta
from tqdm import tqdm
import optparse
import requests
import json

parser = optparse.OptionParser()
parser.add_option('-d', '--date', dest='date',
                  help='Date (YYYYMMDD) to search courts for',
                  default="20211222")

PST_DIFF = timedelta(hours=8)

def parse_input_date(dt_str):
    return datetime.strptime(dt_str, "%Y%m%d")

def parse_schedule_date(dt_str):
    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")

def get_schedule_date_format(dt):
    """
    Given PST datetime, object, returns UTC string
    """
    return datetime.strftime(dt + PST_DIFF,
                             "%Y-%m-%dT%H:%M:%S.%fZ")

def pretty_time_str(dt):
    return datetime.strftime(dt, "%I:%M%p")

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

def get_sched_hour(hour_data):
    is_available = hour_data.get('value', None)
    pst_time = parse_schedule_date(hour_data.get('startDate')) - PST_DIFF
    return is_available, pst_time

def get_court_schedule(court_id, dt):
    sched_data = {
        "reservationId": None,
        "resourceIds": [int(court_id)],
        "date": get_schedule_date_format(dt),
        "dayCount": 1,
        "includeHours": True,
        "includeRentalPoints": True,
        "includeWorkRuleNames": True
    }

    resp = requests.post(COURT_SCHEDULE_URL,
                         headers=HEADERS,
                         json=sched_data)
    schedule = resp.json().get("resources", list())[0] \
                          .get("days")[0] \
                          .get("levels")
    times = list(map(get_sched_hour, schedule))
    return times

def main(date):
    dt = parse_input_date(date)
    print(dt)
    gyms_to_courts = {}
    for gym, gym_id in tqdm(GYM_IDS.items()):
        gyms_to_courts[(gym, gym_id)] = \
            get_courts_from_gym(gym_id)

    all_courts = [court_info for courts in gyms_to_courts.values() \
                             for court_info in courts]
    court_schedules = {}
    for court_name, court_id in tqdm(all_courts):
        court_schedules[court_name] = get_court_schedule(court_id, dt)
        import pdb; pdb.set_trace()

if __name__ == "__main__":
    options, args = parser.parse_args()

    date = str(options.date)
    assert date is not None, "d needs to be a date"
    main(date)

