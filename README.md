# F1NEXT

A simple python script that prints the dates of the next Formula 1 Grand Prix.
It uses [Ergast API](https://ergast.com/mrd) and includes cache to reduce API calls.

![Example of output](https://raw.githubusercontent.com/ralacerda/f1next/main/screenshots/screenshot1.png "Example")

## Usage

```
Usage: f1next [OPTIONS]

  Simple script that shows you information about the next F1 Grand Prix

Options:
  -h, --help                 Show this message and exit.
  -f, --force-download       Force cache to be refreshed.
  -s, --schedule             Show the schedule for all events in the weekend.
  -c, --countdown            Show countdown to the next event
  -i, --circuit-information  Show circuit name and country
  -r, --color                Always printout colors and styling

```


`f1next` will print the name and date of the next Formula 1 Grand Prix.

Use the `-f` or `--force-download` flag to refresh the cache.
The cache lasts for 6 hours, so information about the next Grand Prix might be wrong while another Grand Prix is taking place. This is normal
even if your cache is up to date due to how the Ergast API work.

The `-s` or `--schedule` flag will print the full schedule for the weekend, instead of only showing the first and last dates.
It uses local time as timezone.

The `-c` or `--countdown` flag will also print a countdown in days to the next event. If the event starts in less than 48 hours, it will also print hours and minutes left.

The `-i` or `--circuit-information` flag will print the race circuit name, city and country.

All the options can be used together in any combination and order, except for `-h, --help`.

    f1next -sc
    f1next -s
    f1next -c
    f1next -isc
    f1nxt -si
    f1next -s

![All output options at the same time](https://raw.githubusercontent.com/ralacerda/f1next/main/screenshots/screenshot3.png "All output options")

The script uses `click.echo()` to print out information. If you pipe the output to a file, colors won't be included.
To change this behaviour, include the `-r / --color` flag. It will always print out colors with ANSI escape code.

![Piping to a file](https://raw.githubusercontent.com/ralacerda/f1next/main/screenshots/screenshot2.png "Pipe to file")


### Example of usage

If you are on KDE Plasma, you can use the [command output](https://store.kde.org/p/1166510/) widget to get the output as an HTML panel.   

![Command output usage](https://raw.githubusercontent.com/ralacerda/f1next/main/screenshots/screenshot4.png "Example of usage")

To keep the tables aligned while including colors, you need to change every whitespace to `&nbsp;`:
```
    ~/.local/bin/f1next -scr | sed 's/ /\&nbsp;/g'
```
## Notes

This is a simple hobby project. My main goal was to get familiarity with `python`, `click` and `git`. 
Feel free to open an issue if you have any feedback or features suggestions.

### TODO

- [x] Weekend Schedule 
- [x] Countdown to closest event 
- [x] Option to display more information about the GP 
- [x] Change main function to facilitate testing
- [ ] Publish on PyPI
- [ ] Error handling:
  - [x] API call errors
  - [ ] Can't find next event
  - [ ] Invalid cache
  - [X] Last event is older than 24 hours

### Possible features

- [x] Add `-h` shortcut for help message
- [x] Scheadule table with better formating
- [x] Include round number
- [x] Better color output (grey out past events)
- [ ] ~~Option to open the wikipedia link for the circuit/event~~
- [ ] ~~Emoji Flag~~
