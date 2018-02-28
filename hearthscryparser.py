import argparse
import json
import sys
import datetime

class Parsed_Game:

    def __init__(self,game):
        self.user_hash = game['user_hash']
        self.region = game['region']
        self.game_id = game['id']
        self.unique_id = str(self.region[:2]) + str(self.user_hash) + "-" + str(self.game_id)
        self.mode = game['mode']
        self.s_time = datetime.datetime.strptime(game['added'][:19], '%Y-%m-%dT%H:%M:%S')
        if self.mode == 'ranked':
            self.rank = game['rank']
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

        self.pov_class = game['hero']
        self.opponent_class = game['opponent']
        self.pov_is_first = not game['coin']
        self.result = game['result']

        self.card_history = game['card_history']

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

    def expected_player(self):
        if self.current_player == None:
            if self.pov_is_first:
                self.current_player = 'me'
                return 'me'
            else:
                self.current_player = 'opponent'
                return 'opponent'
        else:
            if self.current_player == 'me':
                self.current_player = 'opponent'
                return 'opponent'
            else:
                self.current_player = 'me'
                return 'me'



    def parse_cards_played(self,time_interval=20):
        self.current_player= None
        self.parsed_card_history = []
        current_time = self.s_time
        self.parsed_card_history.append(('GameStart',current_time.__str__(),None))

        expected_turn = 1

        for card_played in self.card_history:
            current_time+=datetime.timedelta(seconds=time_interval)
            string = ""
            expected_player = self.expected_player()
            while expected_turn<card_played['turn']:
                string+=



            self.parsed_card_history.append(string)

def json_analyser(js_object):
    games = js_object['games']

    ps_games = []

    for game in games:
        ps_games.append(Parsed_Game(game))

    print(len(ps_games))

def routine():

    """"Argument Parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help="JSON file of the HearthScry", type=str)
    parser.add_argument('--time_interval','-t',help="Probal Interval Between Plays in seconds", type=int , default=20 )

    args = parser.parse_args()

    input_file_path = args.input_file

    '''
    MAGIC
    '''
    ifile = open(sys.path[0].__str__()+input_file_path)

    js_object = json.load(ifile)

    ifile.close()

    result = json_analyser(js_object)




if __name__ == '__main__':
    routine()
