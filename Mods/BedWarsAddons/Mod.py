from utils import add_tag


class MOD:
    def __init__(self, Globals):
        """ This is an example mod """
        # data transfer variables
        self.Globals = Globals
        self.G = self.Globals
        self.ModData = Globals.ModData["BedWarsAddons"]
        self.backend = Globals.ui_backend
        self.frontend = Globals.ui_frontend

        # game modes
        self.modes = {
            "solos": "eight_one",
            "doubles": "eight_two",
            "trios": "four_three",
            "fours": "four_four",
            "4vs4": "two_four",
            "lucky-2s": "eight_two_lucky",
            "lucky-4s": "four_four_lucky",
            "armed-2s": "eight_two_armed",
            "armed-4s": "four_four_armed",
            "voidless-2s": "eight_two_voidless",
            "voidless-4s": "four_four_voidless",
            "ultimate-2s": "eight_two_ultimate",
            "ultimate-4s": "four_four_ultimate",
            "rush-2s": "eight_two_rush",
            "rush-4s": "four_four_rush",
            "castle": "castle",
        }

        # set mod data
        self.ModData.name = "BedWarsAddons"
        self.ModData.version = "0.2.1"
        self.ModData.headings = {
            "bw-coins": " Coins ",
            "bw-xp": "     XP     ",
            "bw-fpg": " Finals / game ",
            "bw-bpg": " Beds / game ",
            "bw-adjusted-kd": " AKDR ",
            **{f"bw-{name}-fkdr": " Fkdr" for name in self.modes.keys()},
            **{f"bw-{name}-wlr": " Wlr" for name in self.modes.keys()},
            **{f"bw-{name}-kdr": " Kdr" for name in self.modes.keys()},
        }
        self.ModData.config = {
            "bedwars-addons-layout-set-defaults": False,
            **{f"bedwars-addons-layout-set-defaults-{name}": False for name, mode in self.modes.items()},
        }
        self.ModData.settings = {
            "bedwars-addons-layout-set-defaults": "Adjust layout for overall",  # config name : displayed name
            **{f"bedwars-addons-layout-set-defaults-{name}": f"Adjust layout for {name}" for name, mode in self.modes.items()},
        }
        self.ModData.scopes = {
            "init": self.setup,  # this is part of the setup for the backend ui
            "table-headings": self.ModData.headings,  # this contains any additional table headings
            "on-stat-lookup": self.on_stat_lookup,  # this is called when stats have been requested for a player
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
        # set default bedwars values?
        ideal_headings = None
        if self.G.config["bedwars-addons-layout-set-defaults"]:
            # ideal headings
            ideal_headings = [
                "full-name",
                "party-id",
                "bw-overall-levex",
                "bw-overall-winstreak",
                "bw-overall-fkdr",
                "bw-overall-wlr",
                "bw-adjusted-kd",
                "bw-lvl",
                "hp-lvl",
                "tag",
            ]

            # reset var
            self.G.config["bedwars-addons-layout-set-defaults"] = False

        # check for each mode
        for mode in self.modes.keys():
            # set default bedwars values?
            if self.G.config[f"bedwars-addons-layout-set-defaults-{mode}"]:
                # ideal headings
                ideal_headings = [
                    "full-name",
                    "party-id",
                    "bw-overall-levex",
                    "bw-overall-winstreak",
                    f"bw-{mode}-fkdr",
                    f"bw-{mode}-wlr",
                    f"bw-{mode}-kdr",
                    "bw-lvl",
                    "hp-lvl",
                    "tag",
                ]

                # reset var
                self.G.config[f"bedwars-addons-layout-set-defaults-{mode}"] = False

        # update headings?
        if ideal_headings is not None:
            # set default headings
            self.G.config["headings-main"] = [h for h in ideal_headings if
                                              h in self.G.config["headings-main-names"].keys()]

            # sort by
            self.G.config["sort-by"] = "bw-overall-levex"

    def on_stat_lookup(self, stat_loop_thread, existing_stats, hypixel_data):
        """ This adds additional data to the stats """
        # get bedwars section
        try:
            # attempt to get info
            bwstats = hypixel_data["player"]["stats"]["Bedwars"]
            existing_stats["bw-coins"] = bwstats["coins"]
            existing_stats["bw-xp"] = bwstats["Experience"]
            existing_stats["bw-fpg"] = round(bwstats["final_kills_bedwars"] / max([bwstats["games_played_bedwars"], 1]), 2)
            existing_stats["bw-bpg"] = round(bwstats["beds_broken_bedwars"] / max([bwstats["games_played_bedwars"], 1]), 2)
            existing_stats["bw-adjusted-kd"] = round((bwstats["final_kills_bedwars"] + bwstats["kills_bedwars"]) / max([bwstats["final_deaths_bedwars"] + bwstats["deaths_bedwars"], 1]), 2)

            for name, mode in self.modes.items():
                try:
                    existing_stats[f"bw-{name}-fkdr"] = round(
                        bwstats[f"{mode}_final_kills_bedwars"] / max([bwstats[f"{mode}_final_deaths_bedwars"], 1]), 2)
                except:
                    # key doesnt exist
                    existing_stats[f"bw-{name}-fkdr"] = 0
                try:
                    existing_stats[f"bw-{name}-wlr"] = round(
                        bwstats[f"{mode}_wins_bedwars"] / max([bwstats[f"{mode}_losses_bedwars"], 1]), 2)
                except:
                    # key doesnt exist
                    existing_stats[f"bw-{name}-wlr"] = 0
                try:
                    existing_stats[f"bw-{name}-kdr"] = round(
                        bwstats[f"{mode}_kills_bedwars"] / max([bwstats[f"{mode}_deaths_bedwars"], 1]), 2)
                except:
                    existing_stats[f"bw-{name}-kdr"] = 0

            # tagging?
            if existing_stats["bw-overall-levex"] > 1000:
                add_tag(existing_stats["nick-name"], "BW")

        except Exception as e:
            print("ERROR", e)
            # set defaults
            existing_stats["bw-coins"] = 0
            existing_stats["bw-xp"] = 0
            existing_stats["bw-fpg"] = 0
            existing_stats["bw-bpg"] = 0
            existing_stats["bw-adjusted-kd"] = 0

            for name, mode in self.modes.items():
                existing_stats[f"bw-{name}-fkdr"] = 0
                existing_stats[f"bw-{name}-wlr"] = 0
                existing_stats[f"bw-{name}-kdr"] = 0

        # return the stats
        return existing_stats
