# IRC nick batch renamer tool for Matrix

This script renames IRC nicks of
[Mautrix-telegram](https://github.com/tulir/mautrix-telegram/) users
based on their Telegram user names. This script can be expanded to
rename other puppets as well but currently supports Mautrix-telegram
only.

## Installation

Copy [examples/config.yml](examples/config.yml) from example directory
to the parent directory and edit it to your needs. You need to change
at least the following:

* `token`: Set to as_token of your telegram bot appservice. Copy it
  from mautrix-telegram config file.
* `server`: Set to your homeserver URL (including port)
* `mautrix_telegram_db`: Set to PostgreSQL connect string to
  Mautrix-telegram's database.

### Python requirements

Set up virtualenv or install dependencies globally. This script is so
simple so I suggest installing dependencies from APT.

In Ubuntu and Debian, run:

```sh
sudo apt install python3-yaml python3-psycopg2
```

### PostgreSQL privileges

If your username is *matrix-irc-nick* and database name is
*mautrix-telegrem:

```sql
CREATE USER "matrix-irc-nick";
\c mautrix-telegram
GRANT SELECT ON puppet TO "matrix-irc-nick";
```

### Make it automatic

Copy files `examples/matrix-irc-nick.service` and
`examples/matrix-irc-nick.timer` to `/etc/systemd/system/`. Update
service path and user names in service file and randomize timer
execution time in timer file to somewhere at night time so all servers
using this script are not creating the peak at the same time.

Try once:

```sh
sudo systemctl daemon-reload
sudo systemctl start --no-block matrix-irc-nick.service
sudo journalctl -fu matrix-irc-nick.service
```

If it executes without errors, enable the timer to make it recurring:

```sh
sudo systemctl enable matrix-irc-nick.timer
sudo systemctl start matrix-irc-nick.timer
```

## Adding new supported IRC networks

The script can rename nicknames in any network which supports
appservice `!nick` command. Only requirements are bridge server name,
its room alias format and appservice matrix id.

Add those to config.yml and please submit pull request to make them
mainstream. The required parameters can be found from
[List of bridged IRC networks](https://github.com/matrix-org/matrix-appservice-irc/wiki/Bridged-IRC-networks).

## Maintainer

The first version was written by [vurpo](https://github.com/vurpo) and
has been refactored by [Zouppen](https://github.com/zouppen/). Maintained by
[Hacklab.fi](https://hacklab.fi/) community and actively used on
Hacklab.fi's Matrix home server.
