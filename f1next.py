import click
from datetime import datetime, date
import json
import requests_cache
import appdirs
from pathlib import Path
from dateutil import tz
from math import floor, ceil

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
@click.option("-d", "--hide-date", is_flag=True, default=False)
@click.option("-c", "--hide-countdown", is_flag=True, default=False)
@click.option("-n", "--hide-name", is_flag=True, default=False)
def race(omit, hide_date, hide_countdown, hide_name):
    race_date_time = get_event_time(race_date, race_time)
    days_to_race, time_to_race = get_countdown(race_date_time)

    if days_to_race >= omit:
        echo_intro()
        if not hide_name:
            echo_race_name()
        if days_to_race == 0 and not hide_countdown:
            click.echo("today! ", nl=hide_date)
        elif days_to_race == 1 and not hide_countdown:
            click.echo("tomorrow ", nl=hide_date)
        elif days_to_race > 1 and not hide_countdown:
            click.echo("in " + str(days_to_race) + " days ", nl=hide_date)
        if not hide_date:
            echo_date(race_date_time)
        echo_countdown(time_to_race)


def echo_intro():
    click.echo("The next ", nl=False)
    click.secho("Formula 1 ", fg="bright_red", nl=False)
    click.echo("race is ", nl=False)


def echo_race_name():
    click.echo("the ", nl=False)
    click.secho(race_name, fg="bright_green", nl=False)
    click.echo(" race ", nl=False)


def echo_date(race_date_time):
    click.echo(race_date_time.date().strftime("on %B %d at %I:%M %p"))


def echo_countdown(time_to_race):
    days = time_to_race.days
    hours = floor(time_to_race.seconds / (60 * 60))
    minutes = ceil((time_to_race.seconds / 60) % 60)
    click.echo("in {} days,".format(days), nl=False)
    click.echo(" {} hours and {} minutes".format(hours, minutes))
