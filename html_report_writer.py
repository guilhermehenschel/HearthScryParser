from os import listdir
from parsed_game import *
import json
import plotly.plotly as plt
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot

HEROES = ["Druid","Hunter","Mage","Paladin","Priest","Rogue","Shaman","Warlock","Warrior"]
HERO_POWERS = ["Life Tap", "Armor Up!", "Steady Shot", "Fireblast", "Dagger Mastery", "Totemic Call", "Lesser Heal", "Shapeshift", "Reinforce", "The Coin"]
HERO_COLOR = ['#FF7D0A','#ABD473','#69CCF0','#F58CBA','#555555','#FFF569','#0070DE','#9482C9','#661D1A']

DIR_PATH = "Data/"

def json_analyser(js_object,interval_time = 20):
    games = js_object['games']

    ps_games = []

    for game in games:
        parser = ParsedGame(game, interval_time)
        parser.parse_cards_played()
        ps_games.append(parser)

    return ps_games

if __name__ == '__main__':

    games = []
    lt = listdir("Data/")

    for file in lt:
        if file.endswith('.json'):
            with open(DIR_PATH+str(file),"r") as string_file:
                js_object = json.load(string_file)
                games.extend(json_analyser(js_object))

    all_used_cards = set()
    diferrent_cards_per_day = dict()
    counting_cards_per_day = dict()
    counting_cards = dict()
    games_per_day = dict()
    heroe_games_win_day = dict()
    for game in games:
        date = game.s_time.date()
        set_of_cards = game.cards_used()
        if date in diferrent_cards_per_day:
            card_set = diferrent_cards_per_day[date]
            card_set.update(set_of_cards)
        else:
            diferrent_cards_per_day[date] = set_of_cards
        all_used_cards.update(set_of_cards)

        if date in games_per_day:
            games_per_day[date] += 1
        else:
            games_per_day[date] = 1

        if (date, game.pov_class) in heroe_games_win_day:
            if game.result == "win":
                heroe_games_win_day[(date, game.pov_class)][0] += 1
            heroe_games_win_day[(date, game.pov_class)][1] += 1
        else:
            heroe_games_win_day[(date,game.pov_class)] = [1 if game.result == "win" else 0, 1]

        if (date,game.opponent_class) in heroe_games_win_day:
            if game.result == "loss":
                heroe_games_win_day[(date, game.opponent_class)][0] =heroe_games_win_day[(date, game.opponent_class)][0] + 1
            heroe_games_win_day[(date, game.opponent_class)][1] = heroe_games_win_day[(date, game.opponent_class)][1] + 1
        else:
            heroe_games_win_day[(date,game.opponent_class)] = [1 if game.result == "loss" else 0, 1]


        for card in set_of_cards:
            played_this_game = game.count_played_cards_with_id(card.id)
            if (date, card) in counting_cards_per_day:
                count = counting_cards_per_day[(date, card)]
                count += played_this_game
                counting_cards_per_day[(date, card)] = count
            else:
                counting_cards_per_day[(date, card)] = played_this_game

            #Remove The Coin e Class power
            if card.name in HERO_POWERS:
                continue

            if card in counting_cards and played_this_game != 0 and not card.compare_name("The Coin"):
                counting_cards[card] = counting_cards[card] + played_this_game
            elif played_this_game != 0 and not card.compare_name("The Coin"):
                counting_cards[card] = played_this_game






    # Unique cards Per Day
    list_days = []
    list_count = []
    for (key, values) in diferrent_cards_per_day.items():
        list_days.append(key)
        list_count.append(len(values))

    trace1 = go.Bar(
        x = list_days,
        y = list_count,
        name = "Unique Cards played per day",
        showlegend = True
    )

    dataBar = [trace1]
    # End of Unique cards per day

    # Most Played Cards Start
    most_played_cards = []
    for (card, value) in counting_cards.items():
        most_played_cards.append((card, value))

    most_played_cards = sorted(most_played_cards, key=lambda x: x[1], reverse=True)

    dataMostPlayedCards = []
    for most_played_cards in most_played_cards[0:10]:
        uses_per_day = []
        uses_per_day_perct = []
        for day in list_days:
            if (day, most_played_cards[0]) in counting_cards_per_day:
                uses_per_day.append(counting_cards_per_day[(day, most_played_cards[0])])
                uses_per_day_perct.append(uses_per_day[-1]/games_per_day[day])
            else:
                uses_per_day.append(0)
                uses_per_day_perct.append(0)

        dummy_trace = go.Scatter(
            x=list_days,
            y=uses_per_day_perct,
            name=most_played_cards[0].name,
            showlegend=True
        )
        dataMostPlayedCards.append(dummy_trace)

    # Most Played Cards End

    # Classes Start
    played_Hero = [0 for i in HEROES]
    dataPlayedHero = []
    dataWinHero = []
    dataPlayedHero_Pie = []

    for hero in HEROES:
        wins_per = []
        games_played_day = []
        index_of_hero = HEROES.index(hero)
        for day in list_days:
            if (day, hero) in  heroe_games_win_day:
                (wins, total) = heroe_games_win_day[(day, hero)]
                played_Hero[index_of_hero]+=total
                wins_per.append(wins/total)
                games_played_day.append(total)
            else:
                wins_per.append(0)
                games_played_day.append(0)


        dummy_trace_win = go.Scatter(
            x = list_days,
            y = wins_per,
            name = hero+" wins (%)",
            legendgroup = hero,
            showlegend = True,
            yaxis='y2',
            line = dict(
                color = HERO_COLOR[index_of_hero]
            )
        )

        dummy_trace_total = go.Scatter(
            x=list_days,
            y=games_played_day,
            name=hero + " games recorded",
            legendgroup=hero,
            showlegend=True,
            line = dict(
                color = HERO_COLOR[index_of_hero]
            )
        )
        dataPlayedHero.append(dummy_trace_total)
        #dataWinHero.append(dummy_trace_win)
        dataPlayedHero.append(dummy_trace_win)

    trace_Pie = go.Pie(
        labels = HEROES,
        values=played_Hero,
        domain = {"column": 0},
        textinfo="label+percent+value",
        hole = .4,
        marker=dict(
            colors=HERO_COLOR
        )
    )

    dataPlayedHero_Pie = [trace_Pie]
    # Classes End

    layoutPie = {
        "title": "Played Classes",
        "grid": {"rows": 1, "columns": 1},
        "annotations": [
            {
                "font": {
                    "size": 20
                },
                "showarrow": False,
                "text": "Heroes"

            }
        ]
    }

    layoutLine = dict(
        title='',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7,
                         label='1w',
                         step='day',
                         stepmode='backward'),
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                         label='YTD',
                         step='year',
                         stepmode='todate'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        ),
        legend = {"traceorder": "reversed"}
    )

    layoutHeroeWin = dict(
        title="Class Total Recorded and Win Percentage",
        yaxis=dict(
            title="Total Games"
        ),
        yaxis2=dict(
            title="Win Percentage",
            overlaying='y',
            side='right'
        ),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7,
                         label='1w',
                         step='day',
                         stepmode='backward'),
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                         label='YTD',
                         step='year',
                         stepmode='todate'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        ),
        legend={"traceorder": "reversed"}
    )


    fig0 = dict(data=dataBar, layout=layoutLine)
    aPlot = plot(fig0,
                 config={"displayModeBar": True},
                 show_link=False,
                 include_plotlyjs=False,
                 output_type='div'
                 )

    fig1 = dict(data=dataMostPlayedCards, layout=layoutLine)
    bPlot = plot(fig1,
                 config={"displayModeBar": False},
                 show_link=False,
                 include_plotlyjs=False,
                 output_type='div'
                 )
    fig2 = dict(data=dataPlayedHero_Pie, layout=layoutPie)
    cPlot = plot(fig2,
                 config={"displayModeBar": True},
                 show_link=False,
                 include_plotlyjs=False,
                 output_type='div'
                 )

    fig3 = dict(data=dataPlayedHero, layout=layoutHeroeWin)
    dPlot = plot(fig3,
                 config={"displayModeBar": True},
                 show_link=False,
                 include_plotlyjs=False,
                 output_type='div'
                 )

    html_string = '''
    <html>
        <head>
          <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
          <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css">
          <style>body{ margin:0 100; background:whitesmoke; }</style>
        </head>
        <body>
          <h1>Unique Cards Played</h1>
          ''' + aPlot + '''
          <h1>Mean number of times card played per Game (Top 10)</h1>
          ''' + bPlot + '''
          <h1>Hero Statistics</h1>
          ''' + cPlot + '''
          ''' + dPlot + '''
        </body>
    </html>'''

    with open("report.html", 'w') as f:
        f.write(html_string)