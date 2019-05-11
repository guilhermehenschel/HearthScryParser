import argparse
import json
import sys
import datetime
import csv

class Parsed_Game:

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
            action = self.current_player.__str__()+" - "+card_name.__str__()
            self.parsed_card_history.append((action, current_time.__str__(), turn, card, card_name, card_mana))

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

def json_analyser(js_object,interval_time = 20):
    games = js_object['games']

    ps_games = []

    for game in games:
        parser = Parsed_Game(game,interval_time)
        parser.parse_cards_played()
        ps_games.append(parser)

    return ps_games

def routine():

    """"Argument Parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help="JSON file of the HearthScry", type=str)
    parser.add_argument('--time-interval','-t',help="Probal Interval Between Plays in seconds", type=int , default=20 )
    parser.add_argument('--discrete-time','-b',help="Use turn number instead of time to verify sequence", type=bool, default=False)
    parser.add_argument('--output-file','-o',help='Path for the output file (mode r)', type=str, default='output.csv')
    args = parser.parse_args()

    input_file_path = args.input_file
    time_interval = args.time_interval
    output_file_path = args.output_file


    '''
    MAGIC
    '''
    ifile = open(sys.path[0].__str__()+input_file_path)

    js_object = json.load(ifile)

    ifile.close()

    result = json_analyser(js_object, time_interval)

    with open("event_log_"+output_file_path,mode="w",newline='\n') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['GameId', 'Activity', 'Time', 'Extras'])
        for game in result:
            for line in game.event_log():
                csvwriter.writerow(line)

    with open("Atribute_log_"+output_file_path, mode='w',newline='\n') as csvfile:
        csvwriter = csv.writer(csvfile,quotechar='\'',quoting=csv.QUOTE_NONNUMERIC)
        csvwriter.writerow(['GameId', 'Region', 'Time', 'Mode', 'Rank', 'Class', 'OpponentClass','First', 'NTurns', 'Result'])
        for game in result:
            csvwriter.writerow([game.unique_id,game.region,game.s_time,game.mode,game.rank,game.pov_class,game.opponent_class,int(game.pov_is_first),game.max_turns(),game.result])



if __name__ == '__main__':
    routine()
