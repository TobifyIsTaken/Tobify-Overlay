class MOD:
    def __init__(self, Globals):
        """ This is an example mod """
        # data transfer variables
        self.Globals = Globals
        self.G = self.Globals
        self.ModData = Globals.ModData["BedWarsAddons"]
        self.backend = Globals.ui_backend
        self.frontend = Globals.ui_frontend

        # set mod data
        self.ModData.name = "BedWarsAddons"
        self.ModData.version = "0.0.1"
        self.ModData.headings = {
            "bw-coins": " Coins ",
            "bw-xp": "     XP     ",
            "bw-fpg": " Finals / game ",
            "bw-bpg": " Beds / game ",
        }
        self.ModData.config = {
            "bedwars-addons-layout-set-defaults": False,
        }
        self.ModData.settings = {
            "bedwars-addons-layout-set-defaults": "Adjust layout for bedwars",  # config name : displayed name
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
        if self.G.config["bedwars-addons-layout-set-defaults"]:
            # ideal headings
            ideal_headings = [
                "full-name",
                "party-id",
                "levex",
                "winstreak",
                "fkdr",
                "wlr",
                "kdr",
                "bw-lvl",
                "hp-lvl"
            ]

            # set default headings
            self.G.config["headings-main"] = [h for h in ideal_headings if
                                              h in self.G.config["headings-main-names"].keys()]

            # sort by
            self.G.config["sort-by"] = "levex"

            # reset var
            self.G.config["bedwars-addons-layout-set-defaults"] = False

    def on_stat_lookup(self, stat_loop_thread, existing_stats, hypixel_data):
        """ This adds additional data to the stats """
        # get bedwars section
        try:
            # attempt to get info
            bwstats = hypixel_data["player"]["stats"]["Bedwars"]
            existing_stats["bw-coins"] = bwstats["coins"]
            existing_stats["bw-xp"] = bwstats["Experience"]
            existing_stats["bw-fpg"] = round(bwstats["final_kills_bedwars"] / bwstats["games_played_bedwars"], 2)
            existing_stats["bw-bpg"] = round(bwstats["beds_broken_bedwars"] / bwstats["games_played_bedwars"], 2)
        except Exception as e:
            # set defaults
            existing_stats["bw-coins"] = 0
            existing_stats["bw-xp"] = 0
            existing_stats["bw-fpg"] = 0
            existing_stats["bw-bpg"] = 0

        # return the stats
        return existing_stats
