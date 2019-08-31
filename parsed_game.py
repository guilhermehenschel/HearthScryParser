import datetime
import csv
import json

class Card:
    def __init__(self,name,id):
        self.name = name
        self.id = id

    def compare_name(self,name):
        return str(self.name).lower() == name.lower()

    def compare_id(self,id):
        return  str(self.id).lower() == str(id).lower()

    def __eq__(self, other):
        return str(self.id) == str(other.id)

    def __gt__(self, other):
        return str(self.name) > str(other.name)

    def __hash__(self):
        return hash(self.id)

class Writer:
    def __init__(self,parsed_games,init_file_path,output_file_path):
        init_file = open(init_file_path)
        init_json = json.load(init_file)
        self.export_events = bool(init_json["export_event_log"])
        if init_json["Classes_POV"] and init_json["Classes_POV"][0] != "*":
            self.classes_pov = set(init_json["Classes_POV"])
        else:
            self.classes_pov = ["Hunter", "Rogue", "Mage", "Priest", "Paladin", "Warrior", "Shaman", "Warlock", "Druid"]

        if init_json["excluded_class_POV"] and init_json["excluded_class_POV"][0] != "":
            for pov_class in init_json["excluded_class_POV"]:
                self.classes_pov.remove(pov_class)

        if init_json["Classes_Opponent"] and init_json["Classes_Opponent"][0] != "*":
            self.classes_opponent = set(init_json["Classes_Opponent"])
        else:
            self.classes_opponent = ["Hunter", "Rogue", "Mage", "Priest", "Paladin", "Warrior", "Shaman", "Warlock", "Druid"]

        if init_json["excluded_class_Opponent"] and init_json["excluded_class_Opponent"][0] != "":
            for pov_class in init_json["excluded_class_POV"]:
                self.classes_opponent.remove(pov_class)

        self.attributes = init_json["attributes"]

        self.cards_to_count = init_json["count_cards"]

        self.parsed_games = parsed_games

        self.output_path = output_file_path

        self.modes = init_json["game_mode"]

        self.remove_tainted = bool(init_json["remove_tainted"])

    def write_logs(self):
        files_path = []
        attribute_log = open(self.output_path+"_Attribute_log.csv", mode='w',newline='\n')
        files_path.append(self.output_path+"_Attribute_log.csv")
        attribute_csvwriter = csv.writer(attribute_log,quotechar='\'',quoting=csv.QUOTE_NONNUMERIC)
        event_log = ""  # Forward Declaration
        event_csvwriter = ""  # Forward Declaration
        if self.export_events:
            event_log = open(self.output_path+"_Event_log.csv", mode='w',newline='\n')
            event_csvwriter = csv.writer(event_log)
            event_csvwriter.writerow(['GameId', 'Activity', 'Time', 'Extras'])
            files_path.append(self.output_path + "_Event_log.csv")

        attribute_list = self.attributes
        for card in self.cards_to_count:
            if "name" in card:
                attribute_list.append(str("Count_")+card["name"])
            elif "id" in card:
                attribute_list.append(str("Count_")+card["id"])

        attribute_csvwriter.writerow(attribute_list)

        for parsed_game in self.parsed_games:
            if parsed_game.pov_class not in self.classes_pov:
                continue

            if parsed_game.opponent_class not in self.classes_opponent:
                continue

            if parsed_game.is_tainted() and self.remove_tainted:
                continue

            if parsed_game.mode not in self.modes:
                continue

            if self.export_events:
                for line in parsed_game.event_log():
                    event_csvwriter.writerow(line)

            export_line = []

            for att in self.attributes:
                if att == "unique_id":
                    export_line.append(parsed_game.unique_id)
                elif att == "region":
                    export_line.append(parsed_game.region)
                elif att == "start_time" or att == "s_time" or att == "time":
                    export_line.append(parsed_game.s_time)
                elif att == "mode":
                    export_line.append(parsed_game.mode)
                elif att == "rank":
                    export_line.append(parsed_game.rank)
                elif att == "pov_class":
                    export_line.append(parsed_game.pov_class)
                elif att == "opponent_class":
                    export_line.append(parsed_game.opponent_class)
                elif att == "pov_is_first":
                    export_line.append(int(parsed_game.pov_is_first))
                elif att == "max_turns":
                    export_line.append(parsed_game.max_turns())
                elif att == "result":
                    export_line.append(parsed_game.result)

            for card in self.cards_to_count:
                if "name" in card:
                    export_line.append(parsed_game.count_played_cards_with_name(card["name"]))
                elif "id" in card:
                    export_line.append(parsed_game.count_played_cards_with_id(card["id"]))
                else:
                    export_line.append("ERROR")

            attribute_csvwriter.writerow(export_line)

        attribute_log.close()
        if self.export_events:
            event_log.close()

        return files_path


class ParsedGame:

    def __init__(self,game,interval_time=20):
        self.game = game
        self.interval_time = interval_time
        self.user_hash = self.game['user_hash']
        self.region = self.game['region']
        self.game_id = self.game['id']
        self.unique_id = str(self.region[:2]) + str(self.user_hash) + "-" + str(self.game_id)
        self.mode = self.game['mode']
        self.s_time = datetime.datetime.strptime(game['added'][:19], '%Y-%m-%dT%H:%M:%S')
        if self.mode == 'ranked':
            if not self.game['rank']:
                self.rank = "0"
            else:
                self.rank = self.game['rank']
            self.game_quality = 'Constructed'
        elif self.mode == 'casual':
            self.rank = None
            self.game_quality = 'Constructed'
        elif self.mode == 'arena':
            self.rank = None
            self.game_quality = 'Random'
        else:
            self.rank = None
            self.game_quality = 'Tainted'
        self.pov_class = self.game['hero']
        self.opponent_class = self.game['opponent']
        self.pov_is_first = not self.game['coin']
        self.result = self.game['result']

        self.card_history = game['card_history']

        self.parsed_card_history = []

        self.played_cards = []

    def is_tainted(self):
        return (self.game_quality=='Tainted')

    def is_constructed(self):
        return (self.game_quality=='Constructed')

    def is_arena(self):
        return (self.game_quality=='Random')

    def __str__(self):
        return self.unique_id

    def atributes(self):
        return (self.unique_id,self.region,self.mode,self.rank,self.pov_class,self.opponent_class,self.pov_is_first,self.result)

    def max_turns(self):
        if not self.parsed_card_history:
            self.parse_cards_played(self.interval_time)
        return self.parsed_card_history[-1][2]

    def parse_cards_played(self,time_interval=20):
        self.current_player = None
        self.parsed_card_history = []
        current_time = self.s_time
        self.parsed_card_history.append(('GameStart',current_time.__str__(), 0, None, None, None))

        self.played_cards = []
        for card_played in self.card_history:
            current_time+=datetime.timedelta(seconds=time_interval)
            if card_played["player"] == "me":
                self.current_player = "POV"
            else:
                self.current_player = "Opponent"
            turn = card_played["turn"]
            card = card_played["card"]["id"]
            card_name = card_played["card"]["name"]
            card_mana = card_played["card"]["mana"]
            card_id = card_played["card"]["id"]
            self.played_cards.append(Card(card_name,card_id))
            action = self.current_player.__str__()+" - "+card_name.__str__()
            self.parsed_card_history.append((action, current_time.__str__(), turn, card, card_name, card_mana))

    def count_played_cards_with_name(self,card_name):
        if not self.played_cards:
            self.parse_cards_played()

        count = 0
        for card in self.played_cards:
            if card.compare_name(card_name):
                count+=1

        return count

    def count_played_cards_with_id(self, card_id):
        if not self.played_cards:
            self.parse_cards_played()

        count = 0
        for card in self.played_cards:
            if card.compare_id(card_id):
                count += 1

        return count

    def event_log(self,discrete_time=False):
        ret = []
        for event in self.parsed_card_history:
            loged_event = []
            loged_event.append(self.unique_id)
            loged_event.append(event[0])
            if discrete_time:
                loged_event.append(event[2])
            else:
                loged_event.append(event[1])
            loged_event.append(event[2:])
            ret.append(loged_event)
        return ret

    def cards_used(self):
        if not self.played_cards:
            self.parse_cards_played()

        ret = []
        for card in self.played_cards:
            ret.append(card)

        ret = set(ret)
        return ret