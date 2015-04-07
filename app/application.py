from flask import Flask
from flask import render_template, request, jsonify
import json
import random
import zlib
import os
from datetime import date

json_dir = 'json/'

app = Flask(__name__)

HEADERS = ["Season", "Age", "Tm", "Lg", "Pos", "G", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA", "2P%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]
pHEADERS = ["Season", "Age", "Tm", "Lg", "Pos", "G", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA", "2P%", "EFG", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]

players = os.listdir(json_dir)

def generate_hashes():
    hashdict = dict()
    for i in players:
        hashdict[str(crc(i[:-5]))] = i[:-5]
    with open('hdict', 'w') as hdict:
        json.dump(hashdict, hdict)
    return hashdict

def pick_a_year():
    player = random.choice(players)
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

def pick_all_years():
    player = random.choice(players)
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

def pick_this_year():
    import this_year
    this_year.this_year

def crc(name):
    return zlib.crc32(bytes(name.lower(), 'UTF-8'))

def find_first_year(player):
    try:
        with open('{}{}.json'.format(json_dir, player)) as pjson:
            player_json = json.load(pjson)
    except:
        return None
    return player_json['totals'][1]

def find_this_year(player):
    current_year = date.today().year - 1
    current_season = str(current_year) + '-' + str(current_year%1000 + 1)
    print(current_season)
    print('hit')
    try:
        with open('{}{}.json'.format(json_dir, player)) as pjson:
            player_json = json.load(pjson)
    except:
        return None
    for row in player_json['totals'][1:]:
        if row[0] == current_season:
            return row

def find_best_year(player):
    try:
        with open('{}{}.json'.format(json_dir, player)) as pjson:
            player_json = json.load(pjson)
    except:
        return None
    rows = []
    for row in player_json['totals'][1:]:
        if row[0] == 'Career':
            break
        else:
            rows.append(row)
    def int_if_can(x):
        try:
            return int(x)
        except:
            return 0
    best_scoring_year = max(rows, key = lambda x: int_if_can(x[-1]))
    return best_scoring_year

hashdict = generate_hashes()

@app.route('/')
def hello_world():
    table, player_name = pick_a_year()
    pnum = crc(player_name)
    return render_template("index.html", headers = HEADERS, table=table, pnum=pnum, names=[player[:-5] for player in players])

@app.route('/submit', methods=['GET'])
def submit():
    player = request.args.get('player_name');
    pnum = request.args.get('p_num');
    print(player)
    print(crc(player))
    print(pnum)
    if crc(player) == int(pnum):
        table, player_name = pick_a_year()
        return jsonify(successCode = '1', pnum = crc(player_name), stats = render_template("table.html", headers = HEADERS, table=table))
    else:
        return jsonify(successCode = '0')

@app.route('/giveup', methods=['GET'])
def giveup():
    pnum = request.args.get('p_num')
    old_player_name = hashdict[pnum]
    table, player_name = pick_a_year()
    return jsonify(pnum = crc(player_name), player_name = old_player_name, stats = render_template("table.html", headers = HEADERS, table=table))

@app.route('/crack')
def crack():
    table, player_name = pick_all_years()
    pnum = crc(player_name)
    return render_template("index.html", headers = [HEADERS[0]] + HEADERS[5:], table=table, pnum=pnum)

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
    if mode=='best':
        selector = find_best_year
    elif mode == 'rookie':
        selector = find_first_year
    elif mode == 'recent':
        selector = find_this_year
    else:
        selector = find_best_year
    print(mode)
    ltable = []
    rtable = []
    for name in lnames:
        try:
            best_year = selector(name['value'])
            best_year = [best_year[i] for i in [1,2,4,5,7,8,9,10,11,18,19,20,23,24,25,26,27,29]]
            ltable.append([name['value']]+best_year)
        except:
            pass
    for name in rnames:
        try:
            best_year = selector(name['value'])
            best_year = [best_year[i] for i in [1,2,4,5,7,8,9,10,11,18,19,20,23,24,25,26,27,29]]
            rtable.append([name['value']]+best_year)
        except:
            pass
    return jsonify(lnames = [i[0] for i in ltable], rnames = [i[0] for i in rtable],
        left = ltable, right=rtable, lstats=render_template("dtable.html", headers=['Name'] + f_head, table=ltable),
        rstats=render_template("dtable.html", headers=['Name'] + f_head, table=rtable))

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
    app.run(debug = True)#host = '0.0.0.0')


#print(json.dumps(player_json, sort_keys=True, indent=4, separators=(',', ': ')))
