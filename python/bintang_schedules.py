from config import (
    GYM_IDS,
    BEARER,
    GYM_URL_TEMPLATE,
    COURT_SCHEDULE_URL,
    HEADERS
)
from datetime import datetime, timedelta
from tqdm import tqdm
from io import StringIO
import prettytable
import optparse
import requests
import json
import pandas as pd

parser = optparse.OptionParser()
parser.add_option('-d', '--date', dest='date',
                  help='Date (YYYYMMDD) to search courts for',
                  default="20211222")
parser.add_option('-g', '--gym', dest='gyms',
                  help="Choose gyms you'd like to pull schedules for",
                  action="append")

PST_DIFF = timedelta(hours=8)

def parse_input_date(dt_str):
    """
    Parses date string (YYYYmmdd) and gives you a datetime object
    """
    return datetime.strptime(dt_str, "%Y%m%d")

def parse_schedule_date(dt_str):
    """
    Parses a datetime string (e.g. "2022-01-01T05:00:00Z") and gives you a datetime object
    """
    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")

def get_schedule_date_format(dt):
    """
    Given PST datetime, object, returns UTC string
    """
    return datetime.strftime(dt + PST_DIFF,
                             "%Y-%m-%dT%H:%M:%S.%fZ")

def pretty_time_str(dt):
    """
    Given a datetime object, gets pretty-readable time string (e.g. "8:30PM")
    """
    return datetime.strftime(dt, "%I:%M%p")

def get_courts_from_gym(gym_id):
    """
    Given a gym id, gets all the ids for the courts from that gym

    e.g.
    [('San Carlos Court 1', 30683),
     ('San Carlos Court 2', 30748),
     ('San Carlos Court 3', 30749),
     ('San Carlos Court 4', 30750),
     ('San Carlos Court 5', 30751),
     ('San Carlos Court 6', 30752),
     ('San Carlos Court 7', 30753)]
    """
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
    """
    Given hour data e.g.
    {'color': '',
     'endDate': '2022-01-14T02:00:00Z',
     'name': None,
     'partialReservationColor': '',
     'percentage': 0.6153846153833005,
     'reservationColor': '',
     'shares': 0,
     'startDate': '2022-01-13T18:00:00Z',
     'total': 0,
     'value': 0.0,
     'workRuleId': 0}

    Get the PST time from startDate and a flag for whether the court is available
    """
    is_available = "✅" if hour_data.get('value', None) else "❌"
    pst_time = parse_schedule_date(hour_data.get('startDate')) - PST_DIFF
    return is_available, pst_time

def get_court_schedule(court_id, dt):
    """
    Given the court id and the desired date, get the schedule for the court
    e.g. court_id = 30683; dt = datetime.datetime(2022, 1, 13, 0, 0)
    times:
    [('❌', datetime.datetime(2022, 1, 13, 10, 0)),
     ('✅', datetime.datetime(2022, 1, 13, 18, 0)),
     ('❌', datetime.datetime(2022, 1, 13, 19, 0)),
     ('❌', datetime.datetime(2022, 1, 13, 20, 0)),
     ('✅', datetime.datetime(2022, 1, 13, 21, 0)),
     ('❌', datetime.datetime(2022, 1, 13, 22, 0))]
    """
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

def get_prettytable(df):
    """Returns string representation of the given dataframe"""
    output = StringIO()
    df.to_csv(output)
    output.seek(0)
    pt = prettytable.from_csv(output)
    return pt

def main(date, gyms):
    dt = parse_input_date(date)
    gyms_to_courts = {}

    print("Pulling gym court info for the gyms...")
    # Go through each gym and pull the court ids
    for gym, gym_id in tqdm(GYM_IDS.items()):
        if gym in gyms:
            gyms_to_courts[(gym, gym_id)] = \
                get_courts_from_gym(gym_id)

    # Flatten the court id info because it's easier to deal with
    all_courts = [court_info for courts in gyms_to_courts.values() \
                             for court_info in courts]
    court_schedules = []

    print("Pulling schedules for the courts...")
    # For each court, get the times during which it's free
    for court_name, court_id in tqdm(all_courts):
        court_sched = get_court_schedule(court_id, dt)
        for court_hour in court_sched:
            court_schedules.append((court_name,
                                    court_hour[0],
                                    court_hour[1]))

    # Sadly we have to use pandas (it's a great library, I just don't like making
    # people install stuff) to get the resuts in table, then pretty print it.
    df_court_schedules = pd.DataFrame(court_schedules,
                                      columns=["Name", "Available", "Hour"])
    df_pivot = df_court_schedules.pivot(index="Hour", columns="Name", values="Available").fillna("❌")
    df_pivot = df_pivot.set_index(df_pivot.index.strftime("%I:%M%p")).transpose()
    print(get_prettytable(df_pivot))

if __name__ == "__main__":
    options, args = parser.parse_args()

    date = str(options.date)
    gyms = options.gyms
    gyms = gyms if gyms else list(GYM_IDS.keys())
    assert date is not None, "d needs to be a date"
    main(date, gyms)

