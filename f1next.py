import json
from datetime import datetime
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


def get_event_datetime(event_date: str, event_time: str) -> datetime:
    """A helper function that transforms a date string and a time string into
    a datetime object, with UTC as the timezone
    """
    datetime_format = "%Y-%m-%d %H:%M:%S"
    datetime_string = " ".join([event_date, event_time[:-1]])
    event_date = datetime.strptime(datetime_string, datetime_format)
    event_date = event_date.replace(tzinfo=tz.UTC)
    return event_date


@click.command()
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
def f1next(force_download, schedule, countdown):
    cache_dir = appdirs.user_cache_dir("f1next", "f1next")
    cache_file = "f1next_cache"
    cache_path = Path(cache_dir, cache_file)

    request = requests_cache.CachedSession(cache_path)
    if force_download:
        request.cache.clear()
    api_url = "https://ergast.com/api/f1/current/next.json"
    request_json = request.get(api_url).json()
    next_round = request_json["MRData"]["RaceTable"]["Races"][0]

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

    click.echo("The next ", nl=False)
    click.secho("Formula 1 ", fg="bright_red", nl=False)
    click.echo("weekend is the ", nl=False)
    click.secho(next_round["raceName"], fg="bright_green", nl=False)

    if not schedule:
        click.echo(" on ", nl=False)
        if first_event_day.month == last_event_day.month:
            # If the month are the same, no need to print it twice
            click.echo(first_event_day.strftime("%-d-"), nl=False)
        else:
            click.echo(first_event_day.strftime("%-d %B-"), nl=False)
        click.echo(last_event_day.strftime("%-d %B"))

    else:
        # Line break since last echo didn't include one
        click.echo("")
        for event_name, event_datetime in gp_events.items():

            # Add a space before Practice
            if "Practice" in event_name:
                event_name = event_name[:-8] + " " + event_name[-8:]

            click.echo(event_name.ljust(20), nl=False)
            click.echo(
                event_datetime.astimezone().strftime("%d %b starting at %I:%M %p")
            )

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

                click.echo(f"{event_name} will start in ", nl=False)

                if time_left.days > 1:
                    click.echo(time_left.days, nl=False)
                    click.echo(" days")
                elif time_left.days == 1:
                    click.echo("in 1 day,", nl=False)
                    click.echo("{} hours and {} minutes".format(hours, minutes))
                elif time_left.days == 0:
                    click.echo("{} hours and {} minutes".format(hours, minutes))

                # Break to not print other events
                # It doesn't print anything if it doesn't find an event in the future
                break
