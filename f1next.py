import json
from datetime import date, datetime
from math import ceil, floor
from pathlib import Path

import appdirs
import click
import requests_cache
from dateutil import tz

events = {
    "Race": "Race",
    "Qualifying": "Qualifying",
    "FirstPractice": "Free Practice 1",
    "SecondPractice": "Free Practice 2",
    "ThirdPractice": "Free Practice 3",
    "Sprint": "Sprint Race",
}

current_datetime = datetime.now(tz.gettz())


def download_gp_info(clear=False):
    cache_dir = appdirs.user_cache_dir("f1next", "f1next")
    cache_file = "race_cache"
    cache_path = Path(cache_dir, cache_file)

    request = requests_cache.CachedSession(cache_path)
    if clear:
        request.cache.clear()
    return request.get("https://ergast.com/api/f1/current/next.json").json()


def parse_gp_info(json):
    gp_info = {}
    gp_base_info = json["MRData"]["RaceTable"]["Races"][0]

    gp_info["name"] = gp_base_info["raceName"]
    gp_info["country"] = gp_base_info["Circuit"]["Location"]["country"]
    gp_info["events"] = {}

    gp_info["events"]["Race"] = get_event_time(
        gp_base_info["date"], gp_base_info["time"]
    )

    for key in events.keys():
        if key in gp_base_info:
            gp_info["events"][key] = get_event_time(
                gp_base_info[key]["date"], gp_base_info[key]["time"]
            )

    gp_info["events"] = dict(sorted(gp_info["events"].items(), key=lambda v: v[1]))

    return gp_info


def get_event_time(event_date, event_time):
    date_time_format = "%Y-%m-%d %H:%M:%S"
    date_time_string = " ".join([event_date, event_time[:-1]])
    event_date_time = datetime.strptime(date_time_string, date_time_format)
    event_date_time = event_date_time.replace(tzinfo=tz.UTC)
    return event_date_time


@click.command()
@click.argument("event")
@click.option("-s", "--schedule", "mode", flag_value="schedule")
@click.option("-c", "--countdown", "mode", flag_value="countdown")
@click.option("-f", "--force-download", is_flag=True, default=False)
def f1next(event, mode, force_download):
    gp_info = parse_gp_info(download_gp_info(force_download))

    echo_intro(gp_info)

    if mode == "countdown":
        for event_info in gp_info["events"].keys():
            echo_countdown(gp_info, event_info)

    if mode == "schedule":
        for event_info in gp_info["events"].keys():
            echo_schedule(gp_info, event_info)


def echo_intro(gp_info):
    click.echo("The next ", nl=False)
    click.secho("Formula 1 ", fg="bright_red", nl=False)
    click.echo("weekend is ", nl=False)
    click.echo("the ", nl=False)
    click.secho(gp_info["name"], fg="bright_green")
    # TODO Include country flag


def echo_schedule(gp_info, event_name):
    event_datetime = gp_info["events"][event_name]
    event_local_datetime = event_datetime.astimezone()
    click.echo(events[event_name].ljust(30), nl=False)
    click.echo(event_local_datetime.strftime("    %B %d at %I:%M %p"))


def echo_countdown(gp_info, event_name):
    event_datetime = gp_info["events"][event_name]
    time_left = event_datetime - current_datetime
    hours = floor(time_left.seconds / (60 * 60))
    minutes = ceil((time_left.seconds / 60) % 60)

    if current_datetime < event_datetime:
        click.echo("The ", nl=False)
        click.echo(event_name, nl=False)
        click.echo(" will start in ", nl=False)
        if time_left.days > 1:
            click.echo(time_left, nl=False)
            click.echo("days")
        elif time_left.days == 1:
            click.echo("in 1 day,", nl=False)
            click.echo("{} hours and {} minutes".format(hours, minutes))
        elif time_left.days == 0:
            click.echo("{} hours and {} minutes".format(hours, minutes))


# TODO: Schedule should print the full schedule color coded
# If the event is in the past, countdown should print it in red
# and include information about when it started
