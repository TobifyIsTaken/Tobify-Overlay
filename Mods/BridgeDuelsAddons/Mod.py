class MOD:
    def __init__(self, Globals):
        """ This is an example mod """
        # data transfer variables
        self.Globals = Globals
        self.G = self.Globals
        self.ModData = Globals.ModData["BridgeDuelsAddons"]
        self.backend = Globals.ui_backend
        self.frontend = Globals.ui_frontend

        # set mod data
        self.ModData.name = "BridgeDuelsAddons"
        self.ModData.version = "0.0.1"
        self.ModData.headings = {
            "d-bridge-blocks placed": " Blocks Placed ",
            "d-bridge-bhr": " Bhr ",
            "d-bridge-bow hits": " Bow Hits ",
            "d-bridge-bow shots": " Bow Shots ",
            "d-bridge-mhr": " Mhr ",
            "d-bridge-melee hits": " Melee Hits ",
            "d-bridge-melee swings": " Melee Swings ",
            "d-bridge-kdr": " Kdr ",
            "d-bridge-kills": " Kills ",
            "d-bridge-deaths": " Deaths ",
            "d-bridge-wlr": " Wlr ",
            "d-bridge-wins": " Wins ",
            "d-bridge-losses": " Losses ",
            "d-bridge-goals": " Goals ",
            "d-bridge-ws": " Bridge WS ",
            "d-bridge-best ws": " Best Bridge WS ",
        }
        self.ModData.config = {
            "bridge-duels-addons-layout-set-defaults": False,
        }
        self.ModData.settings = {
            "bridge-duels-addons-layout-set-defaults": "Adjust layout for bridge duels",  # config name : displayed name
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
        # set default bridge duels values?
        if self.G.config["bridge-duels-addons-layout-set-defaults"]:
            # ideal headings
            ideal_headings = [
                "full-name",
                "party-id",
                "d-bridge-wlr",
                "d-bridge-bhr",
                "d-bridge-mhr",
                "d-bridge-kdr",
                "d-bridge-ws",
                "d-bridge-best ws",
                "hp-lvl"
            ]

            # set default headings
            self.G.config["headings-main"] = [h for h in ideal_headings if
                                              h in self.G.config["headings-main-names"].keys()]

            # sort by
            self.G.config["sort-by"] = "d-bridge-wlr"

            # reset var
            self.G.config["bridge-duels-addons-layout-set-defaults"] = False

    def on_stat_lookup(self, stat_loop_thread, existing_stats, hypixel_data):
        """ This adds additional data to the stats """
        # get duels data
        try:
            # basic duels info
            duels = hypixel_data["player"]["stats"]["Duels"]

            # bridge duels info
            existing_stats["d-bridge-blocks placed"] = duels["bridge_duel_blocks_placed"]
            existing_stats["d-bridge-bhr"] = round(duels["bridge_duel_bow_hits"] / duels["bridge_duel_bow_shots"], 2)
            existing_stats["d-bridge-bow hits"] = duels["bridge_duel_bow_hits"]
            existing_stats["d-bridge-bow shots"] = duels["bridge_duel_bow_shots"]
            existing_stats["d-bridge-mhr"] = round(duels["bridge_duel_melee_hits"] / duels["bridge_duel_melee_swings"],
                                                   2)
            existing_stats["d-bridge-melee hits"] = duels["bridge_duel_melee_hits"]
            existing_stats["d-bridge-melee swings"] = duels["bridge_duel_melee_swings"]
            existing_stats["d-bridge-kdr"] = round(
                duels["bridge_duel_bridge_kills"] / duels["bridge_duel_bridge_deaths"], 2)
            existing_stats["d-bridge-kills"] = duels["bridge_duel_bridge_kills"]
            existing_stats["d-bridge-deaths"] = duels["bridge_duel_bridge_deaths"]
            existing_stats["d-bridge-wlr"] = round(duels["bridge_duel_wins"] / duels["bridge_duel_losses"], 2)
            existing_stats["d-bridge-wins"] = duels["bridge_duel_wins"]
            existing_stats["d-bridge-losses"] = duels["bridge_duel_losses"]
            existing_stats["d-bridge-goals"] = duels["bridge_duel_goals"]
            existing_stats["d-bridge-ws"] = duels["current_winstreak_mode_bridge_duel"]
            existing_stats["d-bridge-best ws"] = duels["best_winstreak_mode_bridge_duel"]
        except Exception as e:
            # set defaults
            existing_stats["d-bridge-blocks placed"] = 0
            existing_stats["d-bridge-bhr"] = 0
            existing_stats["d-bridge-bow hits"] = 0
            existing_stats["d-bridge-bow shots"] = 0
            existing_stats["d-bridge-mhr"] = 0
            existing_stats["d-bridge-melee hits"] = 0
            existing_stats["d-bridge-melee swings"] = 0
            existing_stats["d-bridge-kdr"] = 0
            existing_stats["d-bridge-kills"] = 0
            existing_stats["d-bridge-deaths"] = 0
            existing_stats["d-bridge-wlr"] = 0
            existing_stats["d-bridge-wins"] = 0
            existing_stats["d-bridge-losses"] = 0
            existing_stats["d-bridge-goals"] = 0
            existing_stats["d-bridge-ws"] = 0
            existing_stats["d-bridge-best ws"] = 0

        # return the stats
        return existing_stats
