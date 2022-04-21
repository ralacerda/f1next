import click
from datetime import datetime, date
import json
import requests_cache
import appdirs
from pathlib import Path

cache_dir = appdirs.user_cache_dir("f1next", "f1next")
cache_file = "race_cache"
cache_path = Path(cache_dir, cache_file)

request = requests_cache.CachedSession(cache_path)
data = request.get("https://ergast.com/api/f1/current/next.json").json()

next_race = data["MRData"]["RaceTable"]["Races"][0]

race_name = next_race["raceName"]

date_format = "%Y-%m-%d"
race_date = datetime.strptime(next_race["date"], date_format).date()

current_date = datetime.today().date()

days_to_race = (race_date - current_date).days


@click.group()
def f1next():
    pass


@f1next.command()
@click.option("-o", "--omit", default=0)
@click.option("-d", "--hide-date", is_flag=True, default=False)
@click.option("-c", "--hide-countdown", is_flag=True, default=False)
@click.option("-n", "--hide-name", is_flag=True, default=False)
def race(omit, hide_date, hide_countdown, hide_name):
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
            echo_date()


def echo_intro():
    click.echo("The next ", nl=False)
    click.secho("Formula 1 ", fg="bright_red", nl=False)
    click.echo("race is ", nl=False)


def echo_race_name():
    click.echo("the ", nl=False)
    click.secho(race_name, fg="bright_green", nl=False)
    click.echo(" race ", nl=False)


def echo_date():
    click.echo(race_date.strftime("on %B %d"))
