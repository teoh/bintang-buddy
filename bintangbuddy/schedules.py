import concurrent.futures
import copy
from datetime import date, datetime
from io import StringIO

import click
import pandas as pd
import prettytable
import requests
from pytz import timezone
from pytz import utc as UTC
from tqdm import tqdm

from bintangbuddy.config import AUTH_URL, COURT_SCHEDULE_URL, GYM_IDS, GYM_URL_TEMPLATE, HEADERS

PST = timezone("US/Pacific")


def get_bearer_token():
    """
    Obtains a bearer token for authentication
    """
    res = requests.get(AUTH_URL)
    res.raise_for_status()
    return res.text


def get_request_headers():
    """
    Get headers to include with each request
    """
    headers = copy.deepcopy(HEADERS)
    headers["Authorization"] = f"Bearer {get_bearer_token()}"
    return headers


def parse_utc_datetime_str(dt_str):
    """
    Parses a UTC datetime string (e.g. "2022-01-01T05:00:00.000000Z") and gives you a timezone aware (UTC) datetime object
    """
    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def get_utc_datetime_str(tz_aware_dt):
    """
    Given a timezone aware datetime object, returns UTC datetime string (e.g. "2022-01-01T05:00:00.000000Z")
    """
    return datetime.strftime(tz_aware_dt.astimezone(UTC), "%Y-%m-%dT%H:%M:%S.%fZ")


def pretty_time_str(dt):
    """
    Given a datetime object, gets pretty-readable time string (e.g. "8:30PM")
    """
    return datetime.strftime(dt, "%I:%M%p")


def get_courts_from_gym(gym_id, headers):
    """
    Given a gym ID, gets all the IDs for the courts from that gym

    e.g.
    [('San Carlos Court 1', 30683),
     ('San Carlos Court 2', 30748),
     ('San Carlos Court 3', 30749),
     ('San Carlos Court 4', 30750),
     ('San Carlos Court 5', 30751),
     ('San Carlos Court 6', 30752),
     ('San Carlos Court 7', 30753)]
    """
    res = requests.get(GYM_URL_TEMPLATE.format(GYM_ID=gym_id), headers=headers)
    res.raise_for_status()

    courts = []
    for court_info in res.json().get("items", list()):
        courts.append((court_info.get("name"), court_info.get("resourceId")))

    return courts


def get_availability(hour_data):
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
    is_available = "✅" if hour_data.get("value", None) else "❌"
    pst_datetime = parse_utc_datetime_str(hour_data.get("startDate")).astimezone(PST)
    return is_available, pst_datetime


def get_court_schedule(court_id, dt, headers):
    """
    Given the court id and the desired date, get the schedule for the court
    e.g. court_id = 30683; dt = datetime.datetime(2022, 1, 13, 0, 0)
    times:
    [('❌', datetime.datetime(2022, 1, 13, 10, 0, tzinfo=...)),
     ('✅', datetime.datetime(2022, 1, 13, 18, 0, tzinfo=...)),
     ('❌', datetime.datetime(2022, 1, 13, 19, 0, tzinfo=...)),
     ('❌', datetime.datetime(2022, 1, 13, 20, 0, tzinfo=...)),
     ('✅', datetime.datetime(2022, 1, 13, 21, 0, tzinfo=...)),
     ('❌', datetime.datetime(2022, 1, 13, 22, 0, tzinfo=...))]
    """
    sched_data = {
        "reservationId": None,
        "resourceIds": [int(court_id)],
        "date": get_utc_datetime_str(dt),
        "dayCount": 1,
        "includeHours": True,
        "includeRentalPoints": True,
        "includeWorkRuleNames": True,
    }

    resp = requests.post(COURT_SCHEDULE_URL, headers=headers, json=sched_data)
    schedule = resp.json().get("resources", list())[0].get("days")[0].get("levels")
    times = list(map(get_availability, schedule))
    return times


def get_prettytable(df):
    """Returns string representation of the given dataframe"""
    output = StringIO()
    df.to_csv(output)
    output.seek(0)
    pt = prettytable.from_csv(output)
    return pt


def main(dt, gyms):
    headers = get_request_headers()

    click.echo("Pulling court info for the gym(s)...")
    gyms_to_courts = {}
    # Go through each of the requested gyms and pull the court IDs
    for gym in tqdm(gyms):
        gym = gym.lower()
        if gym in GYM_IDS:
            gym_id = GYM_IDS[gym]
            gyms_to_courts[(gym, gym_id)] = get_courts_from_gym(gym_id=gym_id, headers=headers)

    if len(gyms_to_courts) == 0:
        raise click.UsageError(f"Did not find courts in the given gyms: {gyms}")

    # Flatten the court ID info because it's easier to deal with
    all_courts = [court_info for courts in gyms_to_courts.values() for court_info in courts]

    click.echo("Pulling schedules for the courts...")
    court_schedules = []

    # For each court, get the times during which it's free
    with tqdm(total=len(all_courts)) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(get_court_schedule, court_id=court_id, dt=dt, headers=headers): (court_name, court_id) for court_name, court_id in all_courts
            }
            for future in concurrent.futures.as_completed(futures):
                court_name, court_id = futures[future]
                court_sched = future.result()
                for availability, court_hour in court_sched:
                    court_schedules.append((court_name, availability, court_hour))
                pbar.update(1)

    # Sadly we have to use pandas (it's a great library, I just don't like making
    # people install stuff) to get the resuts in table, then pretty print it.
    df_court_schedules = pd.DataFrame(court_schedules, columns=["Name", "Available", "Hour"])
    df_pivot = df_court_schedules.pivot(index="Hour", columns="Name", values="Available").fillna("❌")
    df_pivot = df_pivot.set_index(df_pivot.index.strftime("%I:%M%p")).transpose()
    click.echo(get_prettytable(df_pivot))


@click.command()
@click.option(
    "-d",
    "--date",
    "dt",
    help="Date (YYYY-MM-DD) to search courts for. Defaults to today.",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(date.today()),
)
@click.option(
    "-g",
    "--gym",
    "gyms",
    help="Gyms you'd like to pull schedules for.",
    type=click.Choice(list(GYM_IDS.keys()), case_sensitive=False),
    multiple=True,
)
@click.version_option()
def cli(dt, gyms):
    """Bintang Badminton Court Availability Finder"""
    pst_dt = PST.localize(dt)
    gyms = gyms if gyms else list(GYM_IDS.keys())
    main(dt=pst_dt, gyms=gyms)
