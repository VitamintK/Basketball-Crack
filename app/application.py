from flask import Flask
from flask import render_template, request, jsonify, session
import json
import random
import zlib
import os
import pickle
import re
from collections import defaultdict
from datetime import date
from uuid import uuid4

from config import root_dir
import json_sets
import percentiles

json_dir = root_dir + 'json/'

default_game_set = json_sets.medium

app = Flask(__name__)

HEADERS = ["Season", "Age", "Tm", "Lg", "Pos", "G", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA", "2P%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]
pHEADERS = ["Season", "Age", "Tm", "Lg", "Pos", "G", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA", "2P%", "EFG", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]

players = os.listdir(json_dir)
LEADERBOARD_FILE = 'leaderboard'

def _generate_sid():
        return str(uuid4())

class Leaderboard():
    def __init__(self, leaderboard_file):
        self.lb_file = leaderboard_file
        try:
            with open(self.lb_file,'rb') as lb_file:
                self.leaderboard = pickle.load(lb_file)
        except:
            #lb_file = open(leaderboard_file, 'wb')
            #self.lb_file = lb_file
            self.leaderboard = defaultdict(list)
        self.sorted_leaderboard = []
        self.cache_sorted_leaderboard()
    def add(self, user_name, score, sid):
        print(self.leaderboard)
        self.leaderboard[sid].append((user_name, score))
        self.save_leaderboard()
        self.generate_sorted_leaderboard()
    def save_leaderboard(self):
        with open(self.lb_file,'wb') as lb_file:
            pickle.dump(self.leaderboard, lb_file)
    def generate_sorted_leaderboard(self):
        self.sorted_leaderboard = sorted([max(value, key=lambda x: int(x[1])) for _,value in self.leaderboard.items()], key=lambda x: int(x[1]), reverse=True)
    def cache_sorted_leaderboard(self):
        if len(self.leaderboard) != len(self.sorted_leaderboard):
            self.generate_sorted_leaderboard()
        return self.sorted_leaderboard
    def get_highest_score(self, sid):
        try:
            return max((y[1] for y in self.leaderboard[sid]), key = lambda x: int(x))
        except:
            raise
            return -1
    def __getitem__(self, thing):
        return self.leaderboard[thing]

class User():
    def __init__(self):
        pass
        #self.score = 
        #self.max_score = 

#THERE NEEDS TO BE A GAME OBJECT FEATURING THE MODE, PLAYERNAME, data, PNUM, MAYBE HTML, OR AT LEAST A METHOD TO CREATE HTML.
                #where the init constructor can take in only the mode, and makes everything.  super niceeeeeee
    #collect median time to solution.
class Game():
    pass



leaderboard = Leaderboard(LEADERBOARD_FILE)



def generate_hashes():
    hashdict = dict()
    for i in players:
        hashdict[str(crc(i[:-5]))] = i[:-5]
    with open('hdict', 'w') as hdict:
        json.dump(hashdict, hdict)
    return hashdict

def pick_a_year(game_set = default_game_set, player = None):
    if not player:
        player = random.choice(game_set)
    player_name = player[:-5]
    with open('{}{}'.format(json_dir,player)) as pjson:
        player_json = json.load(pjson)
    rows = []
    for row in player_json['per_game'][1:]:
        if row[0] == 'Career':
            break
        else:
            rows.append(row)
    return [random.choice(rows)], player_name

def pick_all_years(game_set = default_game_set, player = None):
    if not player:
        player = random.choice(game_set)
    else:
        player = player + '.json'
    player_name = player[:-5]
    with open('{}{}'.format(json_dir,player)) as pjson:
        player_json = json.load(pjson)
    rows = []
    for row in player_json['per_game'][1:]:
        if row[0] == 'Career':
            break
        else:
            rows.append(row)
    rows = [[row[0]] + row[5:] for row in rows]
    return rows, player_name

def pick_this_year(game_set = default_game_set):
    json_sets.this_year

def crc(name):
    return zlib.crc32(bytes(name.lower(), 'UTF-8'))

def find_first_year(player, criteria):
    try:
        with open('{}{}.json'.format(json_dir, player)) as pjson:
            player_json = json.load(pjson)
    except:
        return None
    return player_json[criteria][1]

def find_this_year(player, criteria):
    current_year = date.today().year - 1
    current_season = str(current_year) + '-' + str(current_year%1000 + 1)
    print(current_season)
    print('hit')
    try:
        with open('{}{}.json'.format(json_dir, player)) as pjson:
            player_json = json.load(pjson)
    except:
        return None
    for row in player_json[criteria][1:]:
        if row[0] == current_season:
            return row

def find_worst_year(player, criteria):
    try:
        with open('{}{}.json'.format(json_dir, player)) as pjson:
            player_json = json.load(pjson)
    except:
        return None
    rows = []
    trade_years = []
    for row in player_json[criteria][1:]:

        if row[0] == 'Career':
            break
        elif row[0] not in trade_years:
            rows.append(row)
        if row[2] == 'TOT':
            trade_years.append(row[0])
    def float_if_can(x):
        try:
            return float(x)
        except:
            return 100000
    best_scoring_year = min(rows, key = lambda x: float_if_can(x[-1]))
    return best_scoring_year

def find_career_totals(player, criteria):
    try:
        with open('{}{}.json'.format(json_dir, player)) as pjson:
            player_json = json.load(pjson)
    except:
        return None
    rows = []
    for row in player_json[criteria][1:]:
        if row[0] == 'Career':
            return row

def find_best_year(player, criteria):
    try:
        with open('{}{}.json'.format(json_dir, player)) as pjson:
            player_json = json.load(pjson)
    except:
        return None
    rows = []
    for row in player_json[criteria][1:]:
        if row[0] == 'Career':
            break
        else:
            rows.append(row)
    def float_if_can(x):
        try:
            return float(x)
        except:
            return 0
    best_scoring_year = max(rows, key = lambda x: float_if_can(x[-1]))
    return best_scoring_year


hashdict = generate_hashes()

@app.route('/')
def hello_world():
    #sid = _generate_sid

    #MODE = 'one'

    try:
        if not session['username']:
            print(session['username'], ' is the session username')
            session['username'] = _generate_sid()
    except:
        print('NO SESSIONS USERNAME!  generating a new one')
        session['username'] = _generate_sid()
    try:
        max_streak = session['max_streak']
    except:
        max_streak = 0
    print(max_streak)
    session['score'] = 0
    session['most_recent_nonzero_score'] = 0
    table, player_name = pick_a_year()
    print(HEADERS + table)
    table = percentiles.percentalize([HEADERS] + table)
    print(table)
    pnum = crc(player_name)
    return render_template("index.html", mode = 'one', headers = HEADERS, table=table, pnum=pnum, names=[player[:-5] for player in players], max_streak = max_streak)

@app.route('/all/')
def crack():

    #MODE = 'all'
    ######
    try:
        if not session['username']:
            print(session['username'], ' is the session username')
            session['username'] = _generate_sid()
    except:
        print('NO SESSIONS USERNAME!  generating a new one')
        session['username'] = _generate_sid()
    try:
        max_streak = session['max_streak']
    except:
        max_streak = 0
    ####
    table, player_name = pick_all_years()
    pnum = crc(player_name)
    return render_template("index.html", mode = 'all', headers = [HEADERS[0]] + HEADERS[5:], table=table, pnum=pnum, names=[player[:-5] for player in players], max_streak = max_streak)

@app.route('/all/<playernum>')
def crack_with_name(playernum=None):
    try:
        if not session['username']:
            print(session['username'], ' is the session username')
            session['username'] = _generate_sid()
    except:
        print('NO SESSIONS USERNAME!  generating a new one')
        session['username'] = _generate_sid()
    try:
        max_streak = session['max_streak']
    except:
        max_streak = 0
    ####
    table, player_name = pick_all_years(player = hashdict[playernum])
    pnum = crc(player_name)
    return render_template("index.html", mode = 'all', headers = [HEADERS[0]] + HEADERS[5:], table=table, pnum=pnum, names=[player[:-5] for player in players], max_streak = max_streak)


@app.route('/submit', methods=['GET'])
def submit():
    player = request.args.get('player_name').strip();
    pnum = request.args.get('p_num');
    mode = request.args.get('mode')
    print(player)
    #print(crc(player))
    #print(pnum)
    print(session['username'])
    print(session['score'])
    if crc(player) == int(pnum):
        session['score'] += 1
        session['max_streak'] = session['score']
        session['most_recent_nonzero_score'] = session['score']
        if mode == 'all': 
            table, player_name = pick_all_years()
            print(player_name)
            return jsonify(successCode = '1', pnum = crc(player_name), stats = render_template("table.html", headers = [HEADERS[0]] + HEADERS[5:], table=table))
        else:
            table, player_name = pick_a_year()
            print(player_name)
            return jsonify(successCode = '1', pnum = crc(player_name), stats = render_template("table.html", headers = HEADERS, table=table))
    else:
        session['most_recent_nonzero_score'] = session['score']
        session['score'] = 0
        return jsonify(successCode = '0')

@app.route('/giveup', methods=['GET'])
def giveup():
    session['most_recent_nonzero_score'] = session['score']
    session['score'] = 0
    pnum = request.args.get('p_num')
    mode = request.args.get('mode')
    old_player_name = hashdict[pnum]
    if mode == 'all':
        table, player_name = pick_all_years()
        theaders = [HEADERS[0]] + HEADERS[5:]
    else:
        table, player_name = pick_a_year()
        theaders = HEADERS
    return jsonify(pnum = crc(player_name), player_name = old_player_name, stats = render_template("table.html", headers = theaders, table=table))

@app.route('/submit_score', methods=['GET'])
def submit_score():
    user_score = request.args.get('score')
    try:
        user_name = re.sub(r'\W+ ', ' ', request.args.get('name'))
    except:
        user_name = max(leaderboard[session['username']], key = lambda x: int(x[1]))[0]
    print(session['most_recent_nonzero_score'], user_score)
#    if int(session['most_recent_nonzero_score']) >= int(user_score):
    print('over here')
    leaderboard.add(user_name, session['most_recent_nonzero_score'], session['username'])
    return "ah"

@app.route('/get_user_max', methods=['GET'])
def get_user_max():
    u_sid = session['username']
    return jsonify(score = leaderboard.get_highest_score(u_sid))

@app.route('/leaderboard', methods=['GET'])
def leaderboard_():
    return render_template("headerstable.html", headers = ['Player', 'Streak'], table = leaderboard.cache_sorted_leaderboard())

@app.route('/nik')
def nik():
    pass

f_head = [pHEADERS[i] for i in [1,2,4,5,7,8,9,10,11,18,19,20,23,24,25,26,27,29]]
@app.route('/draft')
def draft():
    positions = ["PG", "SG", "G", "SF", "PF", "F", "C", "C", "UTIL", "UTIL", "BENCH", "BENCH", "BENCH"]
    return render_template("draft.html", positions = positions, names = [player[:-5] for player in players], headers = ['Name'] + f_head, table = [])

@app.route('/sub_draft', methods=['GET'])
def sub_draft():
    lnames = json.loads(request.args.get('playerl'))
    rnames = json.loads(request.args.get('playerr'))
    mode = request.args.get('mode')
    criteria = request.args.get('criteria')
    print(criteria)
    if criteria == 'per_game': #FIX THIS SHIT CODE LATER
        relevant_stat_indexes = [1,2,4,5,7,8,9,10,11,17,18,19,22,23,24,25,26,28]
    else:
       relevant_stat_indexes = [1,2,4,5,7,8,9,10,11,18,19,20,23,24,25,26,27,29]
    if mode=='best':
        selector = find_best_year
    elif mode == 'rookie':
        selector = find_first_year
    elif mode == 'recent':
        selector = find_this_year
    elif mode == 'career':
        selector = find_career_totals
    elif mode == 'worst':
        selector = find_worst_year
    else:
        selector = find_best_year
    print(mode)
    ltable = []
    rtable = []
    for name in lnames:
        try:
            best_year = selector(name['value'], criteria)
            best_year = [best_year[i] for i in relevant_stat_indexes]
            ltable.append([name['value']]+best_year)
        except:
            pass
    for name in rnames:
        try:
            best_year = selector(name['value'], criteria)
            best_year = [best_year[i] for i in relevant_stat_indexes]
            rtable.append([name['value']]+best_year)
        except:
            pass
    return jsonify(lnames = [i[0] for i in ltable], rnames = [i[0] for i in rtable],
        left = ltable, right=rtable, lstats=render_template("dtable.html", headers=['Name'] + f_head, table=ltable),
        rstats=render_template("dtable.html", headers=['Name'] + f_head, table=rtable))

@app.route('/a-z')
def alpha():
    import string
    positions = list(string.ascii_uppercase)
    return render_template("draft.html", positions = positions, names = [player[:-5] for player in players], headers = ['Name'] + f_head, table = [])

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

with open(root_dir + 'secret.txt') as j:
    app.secret_key = j.read()
#app.config['SESSION_PATH'] = "/session"
#app.config['SECRET_KEY'] = 'absbdfbdbf'
#skip_paths = ['/static']
#app.session_interface = ManagedSessionInterface(CachingSessionManager(FileBackedSessionManager(app.config['SESSION_PATH'], app.config['SECRET_KEY']), 1000), skip_paths, datetime.timedelta(days=1))

if __name__ == '__main__':
    app.run(debug = True)#host = '0.0.0.0')


#print(json.dumps(player_json, sort_keys=True, indent=4, separators=(',', ': ')))
