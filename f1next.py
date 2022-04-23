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


def download_gp_info():
    cache_dir = appdirs.user_cache_dir("f1next", "f1next")
    cache_file = "race_cache"
    cache_path = Path(cache_dir, cache_file)

    request = requests_cache.CachedSession(cache_path)
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

    print(gp_info)

    return gp_info


def get_event_time(event_date, event_time):
    date_time_format = "%Y-%m-%d %H:%M:%S"
    date_time_string = " ".join([event_date, event_time[:-1]])
    event_date_time = datetime.strptime(date_time_string, date_time_format)
    event_date_time = event_date_time.replace(tzinfo=tz.UTC)
    return event_date_time


def get_countdown(event_date_time, current_date):
    current_date = current_date.replace(tzinfo=tz.gettz())
    days_to_event = event_date_time.date() - current_date.date()
    time_to_event = event_date_time - current_date
    return days_to_event, time_to_event


@click.command()
@click.argument("event")
@click.option("-s", "--schedule", is_flag=True, default=False)
@click.option("-d", "--days", "countdown", flag_value="days")
@click.option("-c", "--countdown", "countdown", flag_value="countdown")
def f1next(event, schedule, countdown):
    current_date = datetime.today()

    gp_info = parse_gp_info(download_gp_info())

    echo_intro(gp_info)

    if not schedule:
        days_to_event, time_to_event = get_countdown(
            gp_info["events"]["Race"], current_date
        )

        click.echo("The race will start in", nl=False)

        echo_countdown_time(time_to_event)

    # if days_to_race >= omit:
    #     echo_intro()
    #     if countdown == "days":
    #         echo_countdown_days(days_to_race)
    #     elif countdown == "countdown":
    #         echo_countdown_time(time_to_race)
    #     elif countdown is None:
    #         echo_countdown(days_to_race, time_to_race)

    #     click.echo()


def echo_intro(gp_info):
    click.echo("The next ", nl=False)
    click.secho("Formula 1 ", fg="bright_red", nl=False)
    click.echo("weekend is ", nl=False)
    click.echo("the ", nl=False)
    click.secho(gp_info["name"], fg="bright_green")


def echo_event(gp_info, event_name):
    pass


def echo_date(race_date_time):
    click.echo(race_date_time.date().strftime("on %B %d at %I:%M %p"), nl=False)


def echo_countdown(days_to_race, time_to_race):
    if days_to_race >= 1:
        echo_countdown_days(days_to_race)
    else:
        echo_countdown_time(time_to_race)


def echo_countdown_days(days_to_race):
    if days_to_race == 0:
        click.echo("today! ", nl=False)
    elif days_to_race == 1:
        click.echo("tomorrow ", nl=False)
    elif days_to_race > 1:
        click.echo("in " + str(days_to_race) + " days ", nl=False)


def echo_countdown_time(time_to_event):
    days = time_to_event.days
    hours = floor(time_to_event.seconds / (60 * 60))
    minutes = ceil((time_to_event.seconds / 60) % 60)
    if days == 1:
        click.echo("in 1 day,", nl=False)
    elif days > 1:
        click.echo(" in {} days,".format(days), nl=False)
    click.echo(" {} hours and {} minutes".format(hours, minutes))
