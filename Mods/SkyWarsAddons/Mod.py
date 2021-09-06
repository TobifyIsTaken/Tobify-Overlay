from functools import lru_cache


def interpolate(xs: list, ys: list, zs: list, ratio: float) -> list:
    """ This interpolates between two points """
    x = xs[1] - xs[0]
    y = ys[1] - ys[0]
    z = zs[1] - zs[0]
    return [xs[0] + x * ratio, ys[0] + y * ratio, zs[0] + z * ratio]


def interpolate_colour(c1: list, c2: list, ratio: float) -> str:
    """ This gets the colour between two colours """
    r, g, b = interpolate([c1[0], c2[0]], [c1[1], c2[1]], [c1[2], c2[2]], ratio)
    return "#" + RGB_to_hex(r) + RGB_to_hex(g) + RGB_to_hex(b)


def RGB_to_hex(code: int) -> str:
    """ This converts an rgb code to a hex code """
    digits = "0123456789ABCDEF"
    return digits[int(code // 16)] + digits[int(code % 16)]


def get_digits(text: str) -> str:
    """ This only keeps digits """
    digits = "0123456789"
    p = 0
    skip = False
    out = ""
    while p != len(text):
        # new character
        if text[p] in digits:
            if skip:
                skip = False
            else:
                out += text[p]
        elif "§" == text[p]:
            skip = True
        else:
            skip = False

        # next p
        p += 1
    return out


class MOD:
    def __init__(self, Globals):
        """ This is an example mod """
        # data transfer variables
        self.Globals = Globals
        self.G = self.Globals
        self.ModData = Globals.ModData["SkyWarsAddons"]
        self.backend = Globals.ui_backend
        self.frontend = Globals.ui_frontend

        # set mod data
        self.ModData.name = "SkyWarsAddons"
        self.ModData.version = "0.0.1"
        self.ModData.config = {
            "sw-text-colour": True,
            "skywars-addons-layout-set-defaults": False,
        }
        self.ModData.settings = {
            "skywars-addons-layout-set-defaults": "Adjust layout for skywars",  # config name : displayed name
        }
        self.ModData.headings = {
            "sw-kdr": " Kdr ",
            "sw-games": " Games Played ",
            "sw-kpg": " Kills / game ",
            "sw-wlr": " Wlr ",
            "sw-ws": " WS ",
            "sw-lvl": " SW Level ",
            "sw-coins": " Coins ",
            "sw-index": " Index ",
        }
        self.ModData.scopes = {
            "init": self.setup,  # this is part of the setup for the backend ui
            "table-headings": self.ModData.headings,  # this contains any additional table headings
            "on-stat-lookup": self.on_stat_lookup,  # this is called when stats have been requested for a player
            "order-colour": self.get_custom_player_colour,  # this determines output colour
            "config-init": self.ModData.config,  # this is a dictionary of all config items which the mod uses
            "config-settings": self.ModData.name,  # this registers the mod for the settings menu
            "settings-update": self.config_update,  # this is called when settings are updated
        }

    def setup(self, frontend, backend):
        """ This is the mod setup function """
        join_fragment = "\n  - "
        print(
            f"{self.ModData.name} {self.ModData.version} has been loaded with scopes:{join_fragment}{join_fragment.join([scope for scope in self.ModData.scopes.keys()])}",
            end="\n\n")
        self.frontend = frontend
        self.backend = backend

    def config_update(self):
        """ This modifies the settings """
        # set default skywars values?
        if self.G.config["skywars-addons-layout-set-defaults"]:
            # set default headings
            self.G.config["headings-main"] = [
                "full-name",
                "party-id",
                "sw-index",
                "sw-ws",
                "sw-kdr",
                "sw-wlr",
                "sw-kpg",
                "sw-lvl",
                "hp-lvl",
                "tag",
            ]

            # sort by
            self.G.config["sort-by"] = "sw-index"

            # reset var
            self.G.config["skywars-addons-layout-set-defaults"] = False

    def on_stat_lookup(self, stat_loop_thread, existing_stats, hypixel_data):
        """ This adds additional data to the stats """
        # get skywars section
        try:
            # attempt to get info
            skywars_stats = hypixel_data["player"]["stats"]["SkyWars"]
            existing_stats["sw-kdr"] = round(skywars_stats["kills"] / max([skywars_stats["deaths"], 1]), 2)
            existing_stats["sw-games"] = skywars_stats["wins"] + skywars_stats["losses"]
            existing_stats["sw-kpg"] = round(skywars_stats["kills"] / max([existing_stats["sw-games"], 1]), 2)
            existing_stats["sw-wlr"] = round(skywars_stats["wins"] / max([skywars_stats["losses"], 1]), 2)
            existing_stats["sw-ws"] = skywars_stats["win_streak"]
            existing_stats["sw-lvl"] = int(get_digits(skywars_stats["levelFormatted"][2:]))
            existing_stats["sw-coins"] = skywars_stats["coins"]
            existing_stats["sw-index"] = round((existing_stats["sw-kdr"] ** 2) * existing_stats["sw-lvl"], 2)
        except Exception as e:
            # set defaults
            existing_stats["sw-kdr"] = 0
            existing_stats["sw-games"] = 0
            existing_stats["sw-kpg"] = 0
            existing_stats["sw-wlr"] = 0
            existing_stats["sw-ws"] = 0
            existing_stats["sw-lvl"] = 0
            existing_stats["sw-coins"] = 0
            existing_stats["sw-index"] = 0

        # return the stats
        return existing_stats

    @lru_cache(maxsize=32)
    def get_custom_player_colour(self, num):
        """ This calculates the player colour """
        if 0 <= num < 1:
            return interpolate_colour([170, 170, 170], [125, 121, 107], num)
        elif 1 <= num < 2:
            return interpolate_colour([125, 121, 107], [92, 86, 60], num - 1)
        elif 2 <= num < 4:
            return interpolate_colour([92, 86, 60], [113, 89, 48], (num - 2) / 2)
        elif 4 <= num < 8:
            return interpolate_colour([113, 89, 48], [118, 98, 28], (num - 4) / 4)
        elif 8 <= num < 16:
            return interpolate_colour([118, 98, 28], [120, 125, 16], (num - 8) / 8)
        elif 16 <= num < 32:
            return interpolate_colour([120, 125, 16], [102, 135, 16], (num - 16) / 16)
        elif 32 <= num < 48:
            return interpolate_colour([102, 135, 16], [19, 138, 19], (num - 32) / 16)
        elif 48 <= num < 64:
            return interpolate_colour([19, 138, 19], [13, 255, 0], (num - 48) / 16)
        elif 64 <= num < 80:
            return interpolate_colour([13, 255, 0], [0, 170, 0], (num - 64) / 16)
        elif 80 <= num < 96:
            return interpolate_colour([0, 170, 0], [255, 255, 85], (num - 80) / 16)
        elif 96 <= num < 112:
            return interpolate_colour([255, 255, 85], [255, 170, 0], (num - 96) / 16)
        elif 112 <= num < 144:
            return interpolate_colour([255, 170, 0], [255, 85, 85], (num - 112) / 32)
        elif 144 <= num < 208:
            return interpolate_colour([255, 85, 85], [190, 110, 110], (num - 144) / 64)
        else:
            return "#FF1111"
