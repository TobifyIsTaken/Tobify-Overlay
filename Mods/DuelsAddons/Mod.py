class MOD:
    def __init__(self, Globals):
        """ This is an example mod """
        # data transfer variables
        self.Globals = Globals
        self.G = self.Globals
        self.ModData = Globals.ModData["DuelsAddons"]
        self.backend = Globals.ui_backend
        self.frontend = Globals.ui_frontend

        # set mod data
        self.ModData.name = "DuelsAddons"
        self.ModData.version = "0.0.1"
        self.ModData.headings = {
            "d-coins": " Coins ",
            "d-kdr": " Kdr ",
            "d-kills": " Kills ",
            "d-deaths": " Deaths ",
            "d-wlr": " Wlr ",
            "d-wins": " Wins ",
            "d-losses": " Losses ",
            "d-bhr": " Bhr ",
            "d-bow hits": "Bow Hits",
            "d-bow shots": "Bow Shots",
            "d-mhr": " Mhr ",
            "d-melee hits": "Melee Hits",
            "d-melee swings": "Melee Swings",
            "d-ws": "Duels WS",
        }
        self.ModData.config = {
            "duels-addons-layout-set-defaults": False,
        }
        self.ModData.settings = {
            "duels-addons-layout-set-defaults": "Adjust layout for duels",  # config name : displayed name
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
        # set default duels values?
        if self.G.config["duels-addons-layout-set-defaults"]:
            # set default headings
            self.G.config["headings-main"] = [
                "full-name",
                "party-id",
                "d-wlr",
                "d-bhr",
                "d-mhr",
                "d-kdr",
                "d-ws",
                "hp-lvl"
            ]

            # sort by
            self.G.config["sort-by"] = "d-wlr"

            # reset var
            self.G.config["duels-addons-layout-set-defaults"] = False

    def on_stat_lookup(self, stat_loop_thread, existing_stats, hypixel_data):
        """ This adds additional data to the stats """
        # get duels data
        try:
            # basic duels info
            duels = hypixel_data["player"]["stats"]["Duels"]
            existing_stats["d-coins"] = duels["coins"]
            existing_stats["d-kdr"] = round(duels["kills"] / duels["deaths"], 2)
            existing_stats["d-kills"] = duels["kills"]
            existing_stats["d-deaths"] = duels["deaths"]
            existing_stats["d-wlr"] = round(duels["wins"] / duels["losses"], 2)
            existing_stats["d-wins"] = duels["wins"]
            existing_stats["d-losses"] = duels["losses"]
            existing_stats["d-bhr"] = round(duels["bow_hits"] / duels["bow_shots"], 2)
            existing_stats["d-bow hits"] = duels["bow_hits"]
            existing_stats["d-bow shots"] = duels["bow_shots"]
            existing_stats["d-blocks placed"] = duels["blocks_placed"]
            existing_stats["d-mhr"] = round(duels["melee_hits"] / duels["melee_swings"], 2)
            existing_stats["d-melee hits"] = duels["melee_hits"]
            existing_stats["d-melee swings"] = duels["melee_swings"]
            existing_stats["d-ws"] = duels["current_winstreak"]
        except Exception as e:
            # set defaults
            existing_stats["d-coins"] = 0
            existing_stats["d-kdr"] = 0
            existing_stats["d-kills"] = 0
            existing_stats["d-deaths"] = 0
            existing_stats["d-wlr"] = 0
            existing_stats["d-wins"] = 0
            existing_stats["d-losses"] = 0
            existing_stats["d-bhr"] = 0
            existing_stats["d-bow hits"] = 0
            existing_stats["d-bow shots"] = 0
            existing_stats["d-mhr"] = 0
            existing_stats["d-melee hits"] = 0
            existing_stats["d-melee swings"] = 0
            existing_stats["d-ws"] = 0

        # return the stats
        return existing_stats
