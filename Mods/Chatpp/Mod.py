class MOD:
    def __init__(self, Globals):
        """ This adds additional message categories to the player detection algorithm """
        # data transfer variables
        self.Globals = Globals
        self.G = self.Globals
        self.ModData = Globals.ModData["Chatpp"]
        self.backend = Globals.ui_backend
        self.frontend = Globals.ui_frontend

        # set mod data
        self.ModData.name = "Chatpp"
        self.ModData.version = "0.0.1"
        self.ModData.config = {
            "chat++-hypixel": True,
            "chat++-bedwars practice": False,
        }
        self.ModData.settings = {
            "chat++-hypixel": "Optimise for Hypixel",  # config name : displayed name
            "chat++-bedwars practice": "Optimise for the Bedwars Practice server",  # config name : displayed name
        }
        self.ModData.scopes = {
            "init": self.setup,  # this is part of the setup for the backend ui
            "config-init": self.ModData.config,  # this is a dictionary of all config items which the mod uses
            "config-settings": self.ModData.name,  # this registers the mod for the settings menu
            "on-message": self.on_message,  # this is called when a chat message appears
        }

    def setup(self, frontend, backend):
        """ This is the mod setup function """
        join_fragment = "\n  - "
        print(
            f"{self.ModData.name} {self.ModData.version} has been loaded with scopes:{join_fragment}{join_fragment.join([scope for scope in self.ModData.scopes.keys()])}",
            end="\n\n")
        self.frontend = frontend
        self.backend = backend

    def on_message(self, timestamp, message):
        """ This processes a message """
        # print(f"{timestamp} : '{message}'")

        # Hypixel
        if self.G.config["chat++-hypixel"]:
            pass

        # Bedwars practice
        ranks = ["[Master]", "[Adept]", "[Trainee]"]
        if self.G.config["chat++-bedwars practice"]:
            # ranked users
            for rank in ranks:
                if f"{rank} " in message:
                    message = message.split(f"{rank} ")[1]
                    username = message.split(" ")[0]
                    self.add_user(username)

            # void message
            if " was hit into the void by " in message:
                if message.endswith(" FINAL KILL!"):
                    username1 = message.split(" ")[0]
                    username2 = message.split(" ")[-3]
                else:
                    username1, *_, username2 = message.split(" ")
                self.add_user(username1)
                self.add_user(username2)

            # void message
            elif message.endswith(" fell into the void."):
                username = message.split(" ")[0]
                self.add_user(username)

            # lives remaining
            elif " has " in message and " lives" in message:
                username, *_ = message.split(" ")
                self.add_user(username)

            # elimination
            elif " has been eliminated" in message:
                username, *_ = message.split(" ")
                self.sub_user(username)

            # server join message
            elif " has joined!" in message:
                *_, username, _, _ = message.split(" ")
                self.add_user(username)

            # server leave message
            elif " has left!" in message:
                *_, username, _, _ = message.split(" ")
                self.sub_user(username)

            # game leave message
            elif message.endswith(" has left the game!"):
                username = message.split(" ")[0]
                self.add_user(username)

            # game start (connecting to lobby)
            elif message.startswith("Connecting to "):
                self.G.lobby_players = []

            # game start (connection successful)
            elif message.startswith("Successfully connected to "):
                self.G.lobby_players = []

            # sending to lobby
            elif message.startswith("Sending you to "):
                self.G.lobby_players = []

            # remove "at"
            elif message == "Join the discord for more info at: ":
                self.sub_user("at")

            # players in game
            elif message.startswith("Players in this game: "):
                players = message.split(": ")[-1].split(" ")
                for player in players:
                    self.add_user(player)

            # block sumo: gold block
            elif message.endswith(" has been on the centre gold block for 5 seconds!"):
                username = message.split(" ")[0]
                self.add_user(username)

            # bedwars
            elif message.startswith("BED DESTRUCTION > ") and " was dismantled by " in message:
                username = message.split(" ")[-1]
                self.add_user(username)

            # else:
            #     for p in self.G.lobby_players:
            #         if p in message:
            #             print(f"{timestamp} : '{message}'")

    def add_user(self, username):
        """ This adds a username to the player list """
        if username not in self.G.lobby_players:
            self.G.lobby_players.append(username)

    def sub_user(self, username):
        """ This removes a username from the player list """
        if username in self.G.lobby_players:
            # remove player
            self.G.lobby_players.remove(username)

            # run mod actions
            self.G.thread_chat_ctx.mod_on_player_leave(username)
