import time


def hhmmsstime(strt):
    """ This converts a string format of the time into seconds """
    try:
        h, m, s = strt.split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)
    except:
        return 0


def double_digit(num):
    """ This returns two string digits """
    if num > 9:
        return str(num)
    else:
        return "0" + str(num)


def spltime(tseconds):
    """ This gets the time in hours, mins and seconds """
    hours = tseconds // 3600
    minutes = int(tseconds / 60) % 60
    seconds = tseconds % 60
    return hours, minutes, seconds


def strtime(tseconds):
    """ This returns the time in string form """
    return ":".join(double_digit(t) for t in spltime(tseconds))


class MOD:
    def __init__(self, Globals):
        """ This is an example mod """
        # data transfer variables
        self.Globals = Globals
        self.G = self.Globals
        self.ModData = Globals.ModData["PlayTime"]
        self.backend = Globals.ui_backend
        self.frontend = Globals.ui_frontend

        # set mod data
        self.ModData.name = "PlayTime"
        self.ModData.version = "0.0.1"
        self.ModData.headings = {
            "pt-playtime-hh:mm:ss": " Session ",
            "pt-playtime-hh:mm": " Session ",
            "pt-playtime-hh": " Session ",
            "pt-playtime-mm:ss": " Session ",
            "pt-total-seconds": " SECONDS ",
        }
        self.ModData.config = {
            "playtime-min-duration": "00:00:00",
            "playtime-max-duration": "00:10:00",
            "playtime-min-cap": True,
            "playtime-max-cap": True,
        }
        self.ModData.settings = {
            "playtime-min-duration": "Minimum hh:mm:ss",
            "playtime-max-duration": "Maximum hh:mm:ss",
            "playtime-min-cap": "Hide below minimum duration",
            "playtime-max-cap": "Hide above maximum duration",
        }
        self.ModData.scopes = {
            "init": self.setup,  # this is part of the setup for the backend ui
            "table-headings": self.ModData.headings,  # this contains any additional table headings
            "on-stat-lookup": self.on_stat_lookup,  # this is called when stats have been requested for a player
            "config-init": self.ModData.config,  # this is a dictionary of all config items which the mod uses
            "config-settings": self.ModData.name,  # this registers the mod for the settings menu
            "settings-update": self.config_update,  # this is called when settings are updated
        }

        # vars
        self.limit_min = 0
        self.limit_max = 0

    def setup(self, frontend, backend):
        """ This is the mod setup function """
        join_fragment = "\n  - "
        print(
            f"{self.ModData.name} {self.ModData.version} has been loaded with scopes:{join_fragment}{join_fragment.join([scope for scope in self.ModData.scopes.keys()])}",
            end="\n\n")
        self.frontend = frontend
        self.backend = backend

        # get caps
        self.get_caps()

    def get_caps(self):
        """ This gets the caps for playtime """
        if "playtime-min-duration" in self.G.config.keys():
            self.limit_min = hhmmsstime(self.G.config["playtime-min-duration"])
        if "playtime-max-duration" in self.G.config.keys():
            self.limit_max = hhmmsstime(self.G.config["playtime-max-duration"])

    def config_update(self):
        """ This modifies the settings """
        # set caps
        self.get_caps()

    def on_stat_lookup(self, stat_loop_thread, existing_stats, hypixel_data):
        """ This adds additional data to the stats """
        # get bedwars section
        try:
            # only continue if the player is online
            if hypixel_data["player"]["lastLogout"] < hypixel_data["player"]["lastLogin"]:
                raise Exception("PLAYTIME SKIPPED (NOT ONLINE)")

            # attempt to get info
            seconds = int(time.time() - hypixel_data["player"]["lastLogin"] / 1000)
            h, m, s = spltime(seconds)

            # don't show stats?
            if self.G.config["playtime-min-cap"]:
                if self.limit_min > seconds:
                    raise Exception("PLAYTIME CAPPED (MIN)")

            if self.G.config["playtime-max-cap"]:
                if self.limit_max < seconds:
                    raise Exception("PLAYTIME CAPPED (MAX)")

            # set stats
            existing_stats["pt-total-seconds"] = seconds
            existing_stats["pt-playtime-hh:mm:ss"] = ":".join([str(h), double_digit(m), double_digit(s)])
            existing_stats["pt-playtime-hh:mm"] = ":".join([str(h), double_digit(m)])
            existing_stats["pt-playtime-mm:ss"] = ":".join([str(m), double_digit(s)])
            existing_stats["pt-playtime-hh"] = str(h)
        except Exception as e:
            # set defaults
            existing_stats["pt-total-seconds"] = ""
            existing_stats["pt-playtime-hh:mm:ss"] = ""
            existing_stats["pt-playtime-hh:mm"] = ""
            existing_stats["pt-playtime-mm:ss"] = ""
            existing_stats["pt-playtime-hh"] = ""

        # return the stats
        return existing_stats
