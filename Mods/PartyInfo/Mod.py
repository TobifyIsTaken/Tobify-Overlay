from functools import lru_cache


class MOD:
    def __init__(self, Globals):
        """ This is an example mod """
        # data transfer variables
        self.Globals = Globals
        self.G = self.Globals
        self.ModData = Globals.ModData["PartyInfo"]
        self.backend = Globals.ui_backend
        self.frontend = Globals.ui_frontend

        # set mod data
        self.ModData.name = "PartyInfo"
        self.ModData.version = "0.1.0"
        self.ModData.config = {
            "party-info-active": False,
            "party-info-friends": True,
            "party-info-guild": True,
            "party-info-levex-adjustment": False,
            "party-info-text-colour": False,
            "party-info-party-colour": True,
        }
        self.ModData.settings = {
            "party-info-active": "Get party info",
            "party-info-friends": "Use friend data",
            "party-info-guild": "Use guild data",
            "party-info-levex-adjustment": "Adjust levex",
            "party-info-text-colour": "Custom player colours",
            "party-info-party-colour": "Highlight team colour",
        }
        self.ModData.headings = {
            "party-id": "Party",
        }
        self.ModData.custom_heading_colours = {
            "party-id": self.get_table_colour
        }
        self.ModData.scopes = {
            "init": self.setup,  # this is part of the setup for the backend ui
            # "update-f": self.updatef,  # this is part of the main update loop for the frontend ui
            "config-init": self.ModData.config,  # this is a dictionary of all config items which the mod uses
            "config-settings": self.ModData.name,  # this registers the mod for the settings menu
            "table-headings": self.ModData.headings,  # this contains any additional table headings
            "table-heading-colours": self.ModData.custom_heading_colours,  # this replaces the default colour picker
            "on-stat-lookup": self.on_stat_lookup,  # this is called when stats have been requested for a player
            "order-colour": self.order_colour,  # this determines output colour
        }

    def setup(self, frontend, backend):
        """ This is the mod setup function """
        join_fragment = "\n  - "
        print(
            f"{self.ModData.name} {self.ModData.version} has been loaded with scopes:{join_fragment}{join_fragment.join([scope for scope in self.ModData.scopes.keys()])}",
            end="\n\n")
        self.frontend = frontend
        self.backend = backend

    def on_stat_lookup(self, stat_loop_thread, existing_stats, hypixel_data):
        """ This adds additional data to the stats """
        # add party data
        if self.G.config["party-info-active"]:
            # if not in your party
            existing_stats["party-id"] = ""

            # get the friends
            friends = self.get_friends(stat_loop_thread, existing_stats)

            # get the guild members
            guild_members = self.get_guild_members(stat_loop_thread, existing_stats)

            # combine (without duplicates)
            related_players = list(set(guild_members + friends))

            # store in stats
            existing_stats["party-info-related-players"] = related_players

            # calculate party levex
            party_levex = 0

            # check for related player in player stats
            players_to_tag = []
            taken_tags = []
            for i, player_stats in enumerate(self.G.gplayer_stats):
                # get the uuid
                if player_stats["uuid"] in related_players:
                    players_to_tag.append(i)

                # party tag
                if player_stats["party-id"] not in taken_tags:
                    taken_tags.append(player_stats["party-id"])

            # get next available party
            next_available_party = 1
            while next_available_party in taken_tags:
                next_available_party += 1

            # if there are players to tag then add them to the party
            extra_players = []
            if len(players_to_tag) != 0:
                # tag all players found
                for player_pos in players_to_tag:
                    # add the tag to any players tagged as being in that player's party
                    existing_party = self.G.gplayer_stats[player_pos]["party-id"]
                    if existing_party != 0 and existing_party != "":
                        for i, player_stats in enumerate(self.G.gplayer_stats):
                            if player_stats["party-id"] == existing_party:
                                # tag the player
                                if player_stats["display-name"].lower() in self.G.config["Party"].lower() or \
                                        player_stats[
                                            "nick-name"].lower() in self.G.config["Party"].lower() or player_stats[
                                    "display-name"].lower() == \
                                        self.G.config["Username"].lower():
                                    # in your party
                                    player_stats["party-id"] = "PARTY"
                                else:
                                    player_stats["party-id"] = next_available_party

                                # add to players
                                extra_players.append(i)

                                # get the levex
                                party_levex += player_stats["bw-overall-levex"]

                    # add tag
                    if self.G.gplayer_stats[player_pos]["display-name"] in self.G.config["Party"] or \
                            self.G.gplayer_stats[player_pos]["nick-name"] in \
                            self.G.config["Party"] or self.G.gplayer_stats[player_pos]["display-name"] == self.G.config[
                        "Username"]:
                        # in your party
                        self.G.gplayer_stats[player_pos]["party-id"] = "PARTY"
                    else:
                        self.G.gplayer_stats[player_pos]["party-id"] = next_available_party

                    # get levex
                    party_levex += self.G.gplayer_stats[player_pos]["bw-overall-levex"]

                # tag the new player
                if existing_stats["display-name"].lower() in self.G.config["Party"].lower() or existing_stats[
                    "nick-name"].lower() in \
                        self.G.config["Party"].lower() or existing_stats["display-name"].lower() == self.G.config[
                    "Username"].lower():
                    # in your party
                    existing_stats["party-id"] = "PARTY"
                else:
                    existing_stats["party-id"] = next_available_party

                # get the new player's levex
                party_levex += existing_stats["bw-overall-levex"]

            # add to players to tag
            players_to_tag += extra_players
            players_to_tag = list(set(players_to_tag))

            # save new levex
            if len(players_to_tag) != 0 and self.G.config["party-info-levex-adjustment"]:
                # modify levex
                party_levex = int(party_levex / (len(players_to_tag) + 1))

                # adjust all players
                for player_pos in players_to_tag:
                    self.G.gplayer_stats[player_pos]["bw-overall-levex"] = party_levex

                # adjust new player
                existing_stats["bw-overall-levex"] = party_levex
        else:
            # add an empty tag
            existing_stats["party-id"] = ""

        # is it me?
        if (self.G.config["Username"].lower() == existing_stats["display-name"].lower() or self.G.config["Username"] ==
            existing_stats["nick-name"].lower()) and self.G.config["Party"] != "":
            existing_stats["party-id"] = "PARTY"

        # return the updated stats
        return existing_stats

    def get_guild_members(self, stat_loop_thread, existing_stats):
        """ This returns a list of all guild members of a player """
        # should friends be retrieved
        if not self.G.config["party-info-guild"]:
            return []

        # get friends
        guild_members = stat_loop_thread.HypixelApiCall(
            f"https://api.hypixel.net/guild?key={self.G.config['hypixel_api_key']}&player={existing_stats['uuid']}").json()

        # check successful
        if guild_members["success"]:
            # simplify into a list of guild members
            guild_members = self.get_guild_uuids(existing_stats["uuid"], guild_members)
        else:
            # nothing
            guild_members = []
        return guild_members

    def get_guild_uuids(self, user, guild_data):
        """ This returns a list of uuids for the friends of the given user """
        # no guild?
        if guild_data["guild"] is None:
            return []

        # get guild members
        guild_list = []
        for data in guild_data["guild"]["members"]:
            if data["uuid"] != user:
                guild_list.append(data["uuid"])
        return guild_list

    def get_friends(self, stat_loop_thread, existing_stats):
        """ This returns a list of all friends of a player """
        # should friends be retrieved
        if not self.G.config["party-info-friends"]:
            return []

        # get friends
        friends = stat_loop_thread.HypixelApiCall(
            f"https://api.hypixel.net/friends?key={self.G.config['hypixel_api_key']}&uuid={existing_stats['uuid']}").json()

        # check successful
        if friends["success"]:
            # simplify into a list of friends
            friends = self.get_friend_uuids(existing_stats["uuid"], friends)
        else:
            # nothing
            friends = []
        return friends

    def get_friend_uuids(self, user, friend_data):
        """ This returns a list of uuids for the friends of the given user """
        friend_list = []
        for data in friend_data["records"]:
            if data["uuidSender"] == user:
                friend_list.append(data["uuidReceiver"])
            else:
                friend_list.append(data["uuidSender"])
        return friend_list

    def order_colour(self, num):
        """ This determines colour coding """
        # should it return a colour
        if self.G.config["party-info-text-colour"]:
            return self.get_custom_player_colour(num)
        else:
            return None

    @lru_cache(maxsize=32)
    def get_custom_player_colour(self, num):
        """ This calculates the player colour """
        # team colours
        if num == "PARTY":
            # gold
            return "#C9BE0B"
        elif num == 1:
            # red
            return "#FF5733"
        elif num == 2:
            # blue
            return "#334DFF"
        elif num == 3:
            # green
            return "#34FF33"
        elif num == 4:
            # yellow
            return "#F4FF33"
        elif num == 5:
            # aqua
            return "#33FFFE"
        elif num == 6:
            # white
            return "#FFFFFF"
        elif num == 7:
            # pink
            return "#FD33FF"
        elif num == 8:
            # gray
            return "#616161"
        else:
            # purple
            return "#9A69F9"

    def get_table_colour(self, pos):
        """ This returns the colour for the player in the table at the position given """
        return self.get_custom_player_colour(self.frontend.player_stats[pos]["party-id"])