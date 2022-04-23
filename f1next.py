import json
from datetime import date, datetime
from math import ceil, floor
from pathlib import Path

import appdirs
import click
import requests_cache
from dateutil import tz

cache_dir = appdirs.user_cache_dir("f1next", "f1next")
cache_file = "race_cache"
cache_path = Path(cache_dir, cache_file)

request = requests_cache.CachedSession(cache_path)
data = request.get("https://ergast.com/api/f1/current/next.json").json()

next_race = data["MRData"]["RaceTable"]["Races"][0]

race_name = next_race["raceName"]
race_time = next_race["time"][:-1]
race_date = next_race["date"]


def get_event_time(event_date, event_time):
    date_time_format = "%Y-%m-%d %H:%M:%S"
    date_time_string = " ".join([event_date, event_time])
    event_date_time = datetime.strptime(date_time_string, date_time_format)
    event_date_time = event_date_time.replace(tzinfo=tz.UTC)
    return event_date_time


def get_countdown(event_date_time):
    current_date = datetime.today()
    current_date = current_date.replace(tzinfo=tz.gettz())

    days_to_race = event_date_time.date() - current_date.date()
    time_to_race = event_date_time - current_date
    return days_to_race.days, time_to_race


def get_gp_events(race_json):
    events = []


@click.group()
def f1next():
    pass


@f1next.command()
@click.option("-o", "--omit", default=0)
@click.option("-s", "--schedule", is_flag=True, default=False)
@click.option("-d", "--days", "countdown", flag_value="days")
@click.option("-c", "--countdown", "countdown", flag_value="countdown")
def race(omit, schedule, countdown):
    race_date_time = get_event_time(race_date, race_time)
    days_to_race, time_to_race = get_countdown(race_date_time)

    if days_to_race >= omit:
        echo_intro()
        if countdown == "days":
            echo_countdown_days(days_to_race)
        elif countdown == "countdown":
            echo_countdown_time(time_to_race)
        elif countdown is None:
            echo_countdown(days_to_race, time_to_race)

        click.echo()


def echo_intro():
    click.echo("The next ", nl=False)
    click.secho("Formula 1 ", fg="bright_red", nl=False)
    click.echo("race is ", nl=False)
    click.echo("the ", nl=False)
    click.secho(race_name, fg="bright_green", nl=False)
    click.echo(" race ", nl=False)


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


def echo_countdown_time(time_to_race):
    days = time_to_race.days
    hours = floor(time_to_race.seconds / (60 * 60))
    minutes = ceil((time_to_race.seconds / 60) % 60)
    if days == 1:
        click.echo("in 1 day,", nl=False)
    elif days > 1:
        click.echo(" in {} days,".format(days), nl=False)
    click.echo(" {} hours and {} minutes".format(hours, minutes), nl=False)
