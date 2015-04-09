from flask import Flask
from flask import render_template, request, jsonify, session
import json
import random
import zlib
import os
from datetime import date

import json_sets

json_dir = 'json/'

game_set = json_sets.easy



app = Flask(__name__)

HEADERS = ["Season", "Age", "Tm", "Lg", "Pos", "G", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA", "2P%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]
pHEADERS = ["Season", "Age", "Tm", "Lg", "Pos", "G", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA", "2P%", "EFG", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]

players = os.listdir(json_dir)

if True:
    import os
    import cPickle as pickle

    import base64
    import hmac
    import hashlib
    import random
    import string

    import datetime
    from uuid import uuid4
    from collections import OrderedDict

    from werkzeug.datastructures import CallbackDict
    from flask.sessions import SessionInterface, SessionMixin


    def _generate_sid():
        return str(uuid4())


    def _calc_hmac(body, secret):
        return base64.b64encode(hmac.new(secret, body, hashlib.sha1).digest())


    class ManagedSession(CallbackDict, SessionMixin):
        def __init__(self, initial=None, sid=None, new=False, randval=None, hmac_digest=None):
            def on_update(self):
                self.modified = True

            CallbackDict.__init__(self, initial, on_update)
            self.sid = sid
            self.new = new
            self.modified = False
            self.randval = randval
            self.hmac_digest = hmac_digest

        def sign(self, secret):
            if not self.hmac_digest:
                self.randval = ''.join(random.sample(string.lowercase+string.digits, 20))
                self.hmac_digest = _calc_hmac('%s:%s' % (self.sid, self.randval), secret)


    class SessionManager(object):
        def new_session(self):
            'Create a new session'
            raise NotImplementedError

        def exists(self, sid):
            'Does the given session-id exist?'
            raise NotImplementedError

        def remove(self, sid):
            'Remove the session'
            raise NotImplementedError

        def get(self, sid, digest):
            'Retrieve a managed session by session-id, checking the HMAC digest'
            raise NotImplementedError

        def put(self, session):
            'Store a managed session'
            raise NotImplementedError


    class CachingSessionManager(SessionManager):
        def __init__(self, parent, num_to_store):
            self.parent = parent
            self.num_to_store = num_to_store
            self._cache = OrderedDict()

        def _normalize(self):
            print "Session cache size: %s" % len(self._cache)
            if len(self._cache) > self.num_to_store:
                while len(self._cache) > (self.num_to_store * 0.8):  # flush 20% of the cache
                    self._cache.popitem(False)

        def new_session(self):
            session = self.parent.new_session()
            self._cache[session.sid] = session
            self._normalize()
            return session

        def remove(self, sid):
            self.parent.remove(sid)
            if sid in self._cache:
                del self._cache[sid]

        def exists(self, sid):
            if sid in self._cache:
                return True
            return self.parent.exists(sid)

        def get(self, sid, digest):
            session = None
            if sid in self._cache:
                session = self._cache[sid]
                if session.hmac_digest != digest:
                    session = None

                # reset order in OrderedDict
                del self._cache[sid]

            if not session:
                session = self.parent.get(sid, digest)

            self._cache[sid] = session
            self._normalize()
            return session

        def put(self, session):
            self.parent.put(session)
            if session.sid in self._cache:
                del self._cache[session.sid]
            self._cache[session.sid] = session
            self._normalize()


    class FileBackedSessionManager(SessionManager):
        def __init__(self, path, secret):
            self.path = path
            self.secret = secret
            if not os.path.exists(self.path):
                os.makedirs(self.path)

        def exists(self, sid):
            fname = os.path.join(self.path, sid)
            return os.path.exists(fname)

        def remove(self, sid):
            print 'Removing session: %s' % sid
            fname = os.path.join(self.path, sid)
            if os.path.exists(fname):
                os.unlink(fname)

        def new_session(self):
            sid = _generate_sid()
            fname = os.path.join(self.path, sid)

            while os.path.exists(fname):
                sid = _generate_sid()
                fname = os.path.join(self.path, sid)

            # touch the file
            with open(fname, 'w'):
                pass

            print "Created new session: %s" % sid

            return ManagedSession(sid=sid)

        def get(self, sid, digest):
            'Retrieve a managed session by session-id, checking the HMAC digest'

            print "Looking for session: %s, %s" % (sid, digest)

            fname = os.path.join(self.path, sid)
            data = None
            hmac_digest = None
            randval = None

            if os.path.exists(fname):
                try:
                    with open(fname) as f:
                        randval, hmac_digest, data = pickle.load(f)
                except:
                    print "Error loading session file"

            if not data:
                print "Missing data?"
                return self.new_session()

            # This assumes the file is correct, if you really want to
            # make sure the session is good from the server side, you
            # can re-calculate the hmac

            if hmac_digest != digest:
                print "Invalid HMAC for session"
                return self.new_session()

            return ManagedSession(data, sid=sid, randval=randval, hmac_digest=hmac_digest)

        def put(self, session):
            'Store a managed session'
            print "Storing session: %s" % session.sid

            if not session.hmac_digest:
                session.sign(self.secret)

            fname = os.path.join(self.path, session.sid)
            with open(fname, 'w') as f:
                pickle.dump((session.randval, session.hmac_digest, dict(session)), f)


    class ManagedSessionInterface(SessionInterface):
        def __init__(self, manager, skip_paths, cookie_timedelta):
            self.manager = manager
            self.skip_paths = skip_paths
            self.cookie_timedelta = cookie_timedelta

        def get_expiration_time(self, app, session):
            if session.permanent:
                return app.permanent_session_lifetime
            return datetime.datetime.now() + self.cookie_timedelta

        def open_session(self, app, request):
            cookie_val = request.cookies.get(app.session_cookie_name)

            if not cookie_val or not '!' in cookie_val:
                # Don't bother creating a cookie for static resources
                for sp in self.skip_paths:
                    if request.path.startswith(sp):
                        return None

                print 'Missing cookie'
                return self.manager.new_session()

            sid, digest = cookie_val.split('!', 1)

            if self.manager.exists(sid):
                return self.manager.get(sid, digest)

            return self.manager.new_session()

        def save_session(self, app, session, response):
            domain = self.get_cookie_domain(app)
            if not session:
                self.manager.remove(session.sid)
                if session.modified:
                    response.delete_cookie(app.session_cookie_name, domain=domain)
                return

            if not session.modified:
                # no need to save an unaltered session
                # TODO: put logic here to test if the cookie is older than N days, if so, update the expiration date
                return

            self.manager.put(session)
            session.modified = False

            cookie_exp = self.get_expiration_time(app, session)
            response.set_cookie(app.session_cookie_name,
                                '%s!%s' % (session.sid, session.hmac_digest),
                                expires=cookie_exp, httponly=True, domain=domain)


def generate_hashes():
    hashdict = dict()
    for i in players:
        hashdict[str(crc(i[:-5]))] = i[:-5]
    with open('hdict', 'w') as hdict:
        json.dump(hashdict, hdict)
    return hashdict

def pick_a_year():
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

def pick_all_years():
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
    rows = [[row[0]] + row[5:] for row in rows]
    return rows, player_name

def pick_this_year():
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

if __name__ == '__main__':
    app.run(debug = True)#host = '0.0.0.0')


#print(json.dumps(player_json, sort_keys=True, indent=4, separators=(',', ': ')))
