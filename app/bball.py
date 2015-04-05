from flask import Flask
from flask import render_template, request, jsonify
import json
import random
import zlib
import os


app = Flask(__name__)

HEADERS = ["Season", "Age", "Tm", "Lg", "Pos", "G", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA", "2P%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]

players = os.listdir("super-json/")

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
    with open('json/{}'.format(player)) as pjson:
        player_json = json.load(pjson)
    rows = []
    for row in player_json['per_game'][1:]:
        if row[0] == 'Career':
            break
        else:
            rows.append(row)
    return [random.choice(rows)], player_name

def crc(name):
    return zlib.crc32(bytes(name.lower(), 'UTF-8'))

hashdict = generate_hashes()

@app.route('/')
def hello_world():
    table, player_name = pick_a_year()
    pnum = crc(player_name)
    return render_template("index.html", headers = HEADERS, table=table, pnum=pnum)

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
    pnum = request.args.get('p_num');
    old_player_name = hashdict[pnum]
    table, player_name = pick_a_year()
    return jsonify(pnum = crc(player_name), player_name = old_player_name, stats = render_template("table.html", headers = HEADERS, table=table))

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
    app.run(debug = True)#host = '0.0.0.0')


#print(json.dumps(player_json, sort_keys=True, indent=4, separators=(',', ': ')))
