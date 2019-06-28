import argparse
import json
import sys

from parsed_game import *

def json_analyser(js_object,interval_time = 20):
    games = js_object['games']

    ps_games = []

    for game in games:
        parser = ParsedGame(game, interval_time)
        parser.parse_cards_played()
        ps_games.append(parser)

    return ps_games

def routine():

    """"Argument Parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help="JSON file of the HearthScry", type=str)
    parser.add_argument('--time-interval','-t',help="Probal Interval Between Plays in seconds", type=int , default=20 )
    parser.add_argument('--discrete-time','-b',help="Use turn number instead of time to verify sequence", type=bool, default=False)
    parser.add_argument('--output-file','-o',help='Path for the output file (mode r)', type=str, default='output')
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

    writer = Writer(result,sys.path[0].__str__()+"/ini",output_file_path)
    writer.write_logs()


if __name__ == '__main__':
    routine()
