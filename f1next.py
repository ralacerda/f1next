import json
from datetime import datetime
from pathlib import Path

import appdirs
import click
import requests_cache
from dateutil import tz

events = [
    "Race",
    "Qualifying",
    "FirstPractice",
    "SecondPractice",
    "ThirdPractice",
    "Sprint",
]


def get_event_date(event_date):
    date_format = "%Y-%m-%d"
    event_date = datetime.strptime(event_date, date_format)
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
def f1next(force_download):
    cache_dir = appdirs.user_cache_dir("f1next", "f1next")
    cache_file = "race_cache"
    cache_path = Path(cache_dir, cache_file)

    request = requests_cache.CachedSession(cache_path)
    if force_download:
        request.cache.clear()
    api_url = "https://ergast.com/api/f1/current/next.json"
    request_json = request.get(api_url).json()
    next_round = request_json["MRData"]["RaceTable"]["Races"][0]

    event_date_list = []

    event_date_list.append(get_event_date(next_round["date"]))

    for key in events:
        if key in next_round:
            event_date_list.append(get_event_date(next_round[key]["date"]))

    first_event_day = min(event_date_list).date()
    last_event_day = max(event_date_list).date()

    click.echo("The next ", nl=False)
    click.secho("Formula 1 ", fg="bright_red", nl=False)
    click.echo("weekend is the ", nl=False)
    click.secho(next_round["raceName"], fg="bright_green", nl=False)
    click.echo(" on ", nl=False)
    if first_event_day.month == last_event_day.month:
        click.echo(first_event_day.strftime("%-d-"), nl=False)
        click.echo(last_event_day.strftime("%-d %B"))
    else:
        click.echo(first_event_day.strftime("%-d %B-"), nl=False)
        click.echo(last_event_day.strftime("%-d %B"))
