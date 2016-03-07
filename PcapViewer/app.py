#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, render_template, request
from flask_socketio import SocketIO
from utils.parser import parse
import os
import json
from database import db_session
from utils.format import get_treemap
import eventlet

from models import User, Session, Stat, Packet

eventlet.monkey_patch()
app = Flask(__name__)
app.config.from_object('config.default')
socketio = SocketIO(app, async_mode='eventlet')

@app.route('/')
def index(pcap = ''):
    """Display home page"""

    users = User.query.all()
    stats = Stat.query.all()
    sessions = Session.query.all()
    treemap = get_treemap(users)
    packets = Packet.query.all()
    return render_template('index.html', pcap=pcap, users=users, stats = stats, sessions=sessions, treemap=treemap, packets=packets)

# @app.route('/list')
# def listPcap():
#     return render_template('list.html')

@socketio.on('uploadPcap')
def upload(data):
    """Upload a new Pcap File"""
    tmpPath = app.config['UPLOAD_FOLDER'] + "tmp.cap"
    with open(tmpPath, 'w') as f:
        f.write(data['fileContent'])
    parse(tmpPath)
    os.remove(tmpPath)
    reloadData()
    socketio.emit('successfullUpload', {'success': 'Got it !'})


def reloadData():
    """Send new data to display to Client"""
    users = []
    sessions = []
    stats = []
    for user in User.query.all():
        users.append(user.as_dict())
    for session in Session.query.all():
        sessions.append(session.as_dict())
    for stat in Stat.query.all():
        stats.append(stat.as_dict())
    data = {
            'users':users,
            'sessions':sessions,
            'stats':stats
            }
    print data['sessions']
    socketio.emit('newData', json.dumps(data))

# Pour l'instant cette fonction n'est pas appelée

@socketio.on('refreshView')
def refreshView(data):
    """Refresh the view filtered by client"""
    sessions = []
    print data['fileContent']
    for session in Session.query.all():
        if session.protocol in data['fileContent']:
            sessions.append(session.as_dict())
    data = {
            'sessions':sessions
            }
    print data["sessions"]
    socketio.emit('newData', json.dumps(data))

@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        print 'ok'
        print vars(request.files['files'])
        tmpPath = app.config['UPLOAD_FOLDER'] + "tmp.cap"
        request.files['files'].save(tmpPath)
        pcap = parse(tmpPath)
        os.remove(tmpPath)

#         except:
#             flash(u"Impossible to download ", "error")
#             return jsonify(error='An error occured')

        return jsonify(success='Pcap uploaded successfully !')

@app.errorhandler(404)
def page_404(error):
    """Display 404 error page"""
    return render_template("404.html"), 404


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    socketio.run(app)


# Syntaxe pour définir un filtre

# @app.template_filter('nom_du_filtre')
# def nom_ici(dist):
#     unite = 'm'
#     if dist > 1000:
#         dist /= 1000.0
#         unite = 'km'
#     return u'{0:.2f}{1}'.format(dist, unite)

# Syntaxe pour passer une fonction au Template
# La fonction s'écrira : format_distance(dist) et appelle formater_distance(dist)

# @app.context_processor
# def passer_aux_templates():
#     def formater_distance(dist):
#         unite = 'm'
#         if dist > 1000:
#             dist /= 1000.0
#             unite = 'km'
#         return u'{0:.2f}{1}'.format(dist, unite)
#     return dict(format_dist=formater_distance)