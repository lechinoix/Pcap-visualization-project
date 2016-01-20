#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from utils import parser, options

app = Flask(__name__)
app.config.from_object('config.default')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload():
    pcap = request.files['pcap']
    nom_fichier = pcap.filename
    if nom_fichier[-5:] != '.html':
        nom_fichier = secure_filename(nom_fichier)
        pcap.save('./uploads/' + nom_fichier)


@app.errorhandler(404)
def ma_page_404(error):
    return render_template("404.html"), 404

if __name__ == '__main__':

    app.run(debug=True)

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
