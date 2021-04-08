# IRC nick batch renamer tool for Matrix

This script renames IRC nicks of puppeting bridge users to more sane
counterparts. The design goal is to make IRC users' life more pleasant by
the following ways:

* **Nick list looks good**. It is easier to see who you are actually talking to. For example umlaut characters and other non-ASCII characters in nicks are not just silently dropped but best effort is done to transliterate them to ASCII.
* **It's easy to see if you can PM to somebody**. Unlike native Matrix users which can talk to IRC users in private, the puppet users cannot handle that. When you see `^something` in the nick, you are warned.
* **Puppet users do not pollute IRC nickspace**. If a Telegram puppet is having a nick *Joe*, he wouldn't steal nick `Joe` on IRC but occupies `Joe|t`instead.

The following puppeting bridges are tested to work with this script:
* [Mautrix-Telegram](https://github.com/tulir/mautrix-telegram)
* [Mautrix-Whatsapp](https://github.com/tulir/mautrix-whatsapp)
* [Matrix Discord Bridge](https://github.com/Half-Shot/matrix-appservice-discord)
* [Matrix-appservice-slack](https://github.com/matrix-org/matrix-appservice-slack)

## Installation

Copy [examples/config.yml](examples/config.yml) from example directory
to the parent directory and edit it to your needs. You need to change
the following global setting:

* `server`: Set to your homeserver URL (including port).

And for every puppeting bridge you need the following:

* `token`: Set to as_token of your puppeting brudge. Copy it
  from your appservice's config file.
* `mxid`: Appservice bot MXID. Used to find the channels where puppets reside.
* `regex`: Pattern to match to user MXIDs to see if it's a puppet.
* `irc_suffix`: String to add to the end of the nickname (such as `|t`)

### Python requirements

Set up virtualenv or install dependencies globally. This script is so
simple so I suggest installing dependencies from APT.

In Ubuntu and Debian, run:

```sh
sudo apt install python3-yaml python3-unidecode
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

Add those to [config.yaml](examples/config.yaml) and please submit pull request to make them
mainstream. The required parameters can be found from
[List of bridged IRC networks](https://github.com/matrix-org/matrix-appservice-irc/wiki/Bridged-IRC-networks).

## If you plan to run this

If you plan to run this, it will compete with Hacklab Finlands instance
on IRCNet.
That leads to messy behaviour on both sides. We would
like to coordinate this somehow so please contact us first. On private
IRC networks there is no problem.

## Maintainer

The first version was written by [vurpo](https://github.com/vurpo) and
has been refactored by [Zouppen](https://github.com/zouppen/). Maintained by
[Hacklab.fi](https://hacklab.fi/) community and actively used on
Hacklab.fi's Matrix home server.
