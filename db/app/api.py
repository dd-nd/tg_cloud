from flask import Flask, jsonify, render_template
import sqlite3 as sq
import json
from http.server import SimpleHTTPRequestHandler
from http.server import HTTPServer
from waitress import serve

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

class MyHTTPRequestHandler(SimpleHTTPRequestHandler): 
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

@app.route('/getTypesData', methods=['POST'])
def getTypesData():
    with sq.connect('db/database.db') as con: 
        cur = con.cursor()
        cur.execute('SELECT * FROM types;')
        data = [{'id': i[0], 'name': i[1]} for i in cur.fetchall()]
        data = json.dumps(data)
    return data


@app.route('/getGenresData', methods=['POST'])
def getGenresData():
    with sq.connect('db/database.db') as con: 
        cur = con.cursor()
        cur.execute('SELECT * FROM genres;')
        data = [{'id': i[0], 'name': i[1]} for i in cur.fetchall()]
        data = json.dumps(data)
    return data


@app.route('/getStatusesData', methods=['POST'])
def getStatusesData():
    with sq.connect('db/database.db') as con: 
        cur = con.cursor()
        cur.execute('SELECT * FROM statuses;')
        data = [{'id': i[0], 'name': i[1]} for i in cur.fetchall()]
        data = json.dumps(data)
    return data


if __name__ == '__main__':
    app.run(host='localhost', port=8000)