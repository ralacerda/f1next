import json
from datetime import datetime
from functools import partial
from math import ceil, floor
from pathlib import Path

import appdirs
import click
import requests_cache
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
    request_json = request.get(api_url).json()
    return request_json["MRData"]["RaceTable"]["Races"][0]


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
    default=False,
    help="Force cache to be refreshed.",
)
@click.option(
    "-s",
    "--schedule",
    is_flag=True,
    default=False,
    help="Show the schedule for all events in the weekend.",
)
@click.option(
    "-c",
    "--countdown",
    is_flag=True,
    default=False,
    help="Show countdown to the next event",
)
@click.option(
    "-i",
    "--circuit-information",
    is_flag=True,
    default=False,
    help="Show circuit name and country",
)
@click.option("-t", "test_json", hidden=True, default=None, type=click.File())
def f1next(force_download, schedule, countdown, circuit_information, test_json):
    """Simple script that shows you information about the next F1 Grand Prix"""

    if test_json:
        next_round = json.load(test_json)["MRData"]["RaceTable"]["Races"][0]
    else:
        next_round = get_json(force_download)

    gp_events = {}

    # Date of the next round refers to the next race date
    gp_events["Race"] = get_event_datetime(next_round["date"], next_round["time"])

    # Other events are in their own dictionaries
    for key in events:
        # We need to check the key because not all weekends have Sprint
        # or Third Practice
        if key in next_round:
            gp_events[key] = get_event_datetime(
                next_round[key]["date"], next_round[key]["time"]
            )

    gp_events = dict(sorted(gp_events.items(), key=lambda v: v[1]))

    first_event_day = min(list(gp_events.values()))
    last_event_day = max(list(gp_events.values()))

    echo = partial(click.secho)

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
        echo("at the ", nl=False)
        click.secho(f"{circuit_name}, {circuit_city}, {circuit_country}", bold=True)

    if schedule:
        # Line break for better ouput
        echo("")

        # Headears and a line
        echo("Event".ljust(30) + "Date and local time")
        echo("-----".ljust(30) + "-------------------")

        for event_name, event_datetime in gp_events.items():

            # Add a space before Practice
            if "Practice" in event_name:
                event_name = event_name[:-8] + " " + event_name[-8:]

            echo(event_name.ljust(30), nl=False)
            echo(event_datetime.astimezone().strftime("%d %b starting at %I:%M %p"))

        # Footer line
        echo("----")

        # I coud not find a easy way to show timezone name
        # Easiest solution is to show the UTC offset
        # We include de ":" because "%z" return +HHMM or -HHMM
        zone_offset = zone = gp_events["Race"].astimezone().strftime("%z")
        echo("Showing times for UTC" + zone_offset[:3] + ":" + zone_offset[3:])

    if countdown:
        current_datetime = datetime.now().replace(tzinfo=tz.gettz())

        # Looking for the first event that has not started yet
        for event_name, event_datetime in gp_events.items():
            if event_datetime > current_datetime:
                time_left = event_datetime - current_datetime
                hours = floor(time_left.seconds / (60 * 60))
                minutes = ceil((time_left.seconds / 60) % 60)

                # Add a space before Practice
                if "Practice" in event_name:
                    event_name = event_name[:-8] + " " + event_name[-8:]

                echo(f"{event_name} will start in ", nl=False)

                if time_left.days > 1:
                    echo(time_left.days, nl=False)
                    echo(" days")
                elif time_left.days == 1:
                    echo("in 1 day,", nl=False)
                    echo("{} hours and {} minutes".format(hours, minutes))
                elif time_left.days == 0:
                    echo("{} hours and {} minutes".format(hours, minutes))

                # Break to not print other events
                # It doesn't print anything if it doesn't find an event in the future
                break
