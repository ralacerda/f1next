import json
from datetime import datetime, timedelta
from functools import partial
from math import ceil, floor
from pathlib import Path

import appdirs
import click
import requests_cache
import requests
from dateutil import tz

# List of possible events
events = [
    "Race",
    "Qualifying",
    "FirstPractice",
    "SecondPractice",
    "ThirdPractice",
    "Sprint",
]


def get_json(force_download: bool) -> dict:
    """A function that returns information about the next round.

    It sets up a cache file for requests
    If force_download is True, it deletes the cache first
    It returns only the dictonary with information about the next round
    """

    cache_dir = appdirs.user_cache_dir("f1next", "f1next")
    cache_file = "f1next_cache"
    cache_path = Path(cache_dir, cache_file)

    request = requests_cache.CachedSession(cache_path)
    if force_download:
        request.cache.clear()
    api_url = "https://ergast.com/api/f1/current/next.json"

    try:
        response = request.get(api_url)
        response.raise_for_status()
    except requests.exceptions.Timeout as e:
        print("Connection error")
        request.cache.clear()
        exit(1)
    except requests.exceptions.RequestException as e:
        # print(e)
        print("Error downloading data")
        request.cache.clear()
        exit(1)
    return response.json()["MRData"]["RaceTable"]["Races"][0]


def get_countdown_string(time_left: timedelta) -> str:
    """This function produces a string based on
    the time left for the event.

    It takes a `timedelta` object and returns a string
    with days, hours and minutes.
    """

    countdown_string = ""

    # `deltatime` objects only includes days and seconds
    # so we calculate hours and minutes ourselves
    # rounding down hours and rounding up minutes
    countdown_time = {
        "day": time_left.days,
        "hour": floor(time_left.seconds / (60 * 60)),
        "minute": ceil((time_left.seconds / 60) % 60),
    }

    for unit, amount in countdown_time.items():
        # We only print if the amount if higher than 0
        if amount > 0:
            countdown_string += f"{amount} {unit}"
            # If amount if higher than 1, we include the "s" for plural
            countdown_string += "s " if amount > 1 else " "

    return countdown_string


def get_event_datetime(event_date: str, event_time: str) -> datetime:
    """A helper function that returns a timezone aware datetime.

    It transforms a date string and a time string into
    a datetime object, with UTC as the timezone
    """

    datetime_format = "%Y-%m-%d %H:%M:%S"
    datetime_string = " ".join([event_date, event_time[:-1]])
    event_date = datetime.strptime(datetime_string, datetime_format)
    event_date = event_date.replace(tzinfo=tz.UTC)
    return event_date


@click.command()
@click.help_option("-h", "--help")
@click.option(
    "-f",
    "--force-download",
    is_flag=True,
    help="Force cache to be refreshed.",
)
@click.option(
    "-s",
    "--schedule",
    is_flag=True,
    help="Show the schedule for all events in the weekend.",
)
@click.option(
    "-c",
    "--countdown",
    is_flag=True,
    help="Show countdown to the next event",
)
@click.option(
    "-i",
    "--circuit-information",
    is_flag=True,
    help="Show circuit name and country",
)
@click.option(
    "-r",
    "--color",
    is_flag=True,
    default=None,
    help="Always printout colors and styling",
)
@click.option("-t", "test_json", hidden=True, default=None, type=click.File())
def f1next(force_download, schedule, countdown, circuit_information, color, test_json):
    """Simple script that shows you information about the next F1 Grand Prix"""

    if test_json:
        next_round = json.load(test_json)["MRData"]["RaceTable"]["Races"][0]
    else:
        next_round = get_json(force_download)

    gp_events = {}

    # Date of the next round refers to the race date
    gp_events["Race"] = get_event_datetime(next_round["date"], next_round["time"])

    # Other events are in their own dictionaries
    for key in events:
        # We need to check the key because not all weekends have Sprint
        # or Third Practice
        if key in next_round:
            gp_events[key] = get_event_datetime(
                next_round[key]["date"], next_round[key]["time"]
            )

    # We sort the dictionary because events are not always the same order
    # Mainly, Second Practice is not always right after First Practice
    gp_events = dict(sorted(gp_events.items(), key=lambda v: v[1]))

    first_event_day = min(list(gp_events.values()))
    last_event_day = max(list(gp_events.values()))

    # If the `color` flag is `None` (default), `click.secho`
    # will only print color codes if it detects a interactive terminal
    # Setting `color` to `True` will always print ANSI escape colors
    echo = partial(click.secho, color=color)

    echo("The next ", nl=False)
    echo("Formula 1 ", fg="bright_red", nl=False)
    echo("weekend is the ", nl=False)
    echo(next_round["raceName"], fg="bright_green", nl=False)

    if not schedule:
        echo(" on ", nl=False)
        if first_event_day.month == last_event_day.month:
            # If the month are the same, no need to print it twice
            echo(first_event_day.strftime("%-d-"), nl=False)
        else:
            echo(first_event_day.strftime("%-d %B-"), nl=False)
        echo(last_event_day.strftime("%-d %B"), nl=False)

    # Linebreak
    echo("")

    if circuit_information:
        circuit = next_round["Circuit"]
        circuit_name = next_round["Circuit"]["circuitName"]
        circuit_city = next_round["Circuit"]["Location"]["locality"]
        circuit_country = next_round["Circuit"]["Location"]["country"]

        echo(f"Round {next_round['round']}", nl=False)
        echo(" at the ", nl=False)
        echo(f"{circuit_name}, {circuit_city}, {circuit_country}", bold=True)

    # current_datetime is used both in schedule and countdown options
    current_datetime = datetime.now().replace(tzinfo=tz.gettz())

    if schedule:
        # Line break for better ouput
        echo("")

        # I coud not find a easy way to show timezone names
        # Easiest solution is to show the UTC offset
        # We include de ":" because "%z" returns +HHMM or -HHMM
        zone_offset = zone = gp_events["Race"].astimezone().strftime("%z")
        zone_offset = zone_offset[:3] + ":" + zone_offset[3:]

        # Headears and a line
        echo("Event".ljust(25) + f"Date and Time (UTC{zone_offset})")
        echo("-----".ljust(25) + "-------------------")

        next_event = None

        for event_name, event_datetime in gp_events.items():

            # Add a space before "Practice"
            if "Practice" in event_name:
                event_name = event_name[:-8] + " " + event_name[-8:]

            echo(event_name.ljust(25), nl=False)

            # Events in the future are higher
            if event_datetime.astimezone() > current_datetime:
                if not next_event:
                    event_color = "bright_green"
                    next_event = event_name
                else:
                    event_color = None
            else:
                event_color = 238

            echo(
                event_datetime.astimezone().strftime("%d %b starting at %I:%M %p"),
                fg=event_color,
            )

    if countdown:

        # Blank line first
        echo("")

        # Looking for the first event that has not started yet
        for event_name, event_datetime in gp_events.items():
            if event_datetime > current_datetime:

                # Add a space before Practice
                if "Practice" in event_name:
                    event_name = event_name[:-8] + " " + event_name[-8:]

                echo(f"{event_name} will start in ", nl=False)
                echo(get_countdown_string(event_datetime - current_datetime))

                # Break to not print other events
                # It doesn't print anything if it doesn't find an event in the future
                break

    # We exit the `f1next` command with a sucess code
    exit(0)
