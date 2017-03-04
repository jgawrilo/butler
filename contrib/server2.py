from flask import Flask, request
from socketIO_client import SocketIO, LoggingNamespace
from json import loads, dumps

app = Flask(__name__)

socketIO = SocketIO('localhost', 3000, LoggingNamespace)

@app.route('/save_export/', methods=['GET'])
def handle_save():
    if request.method == "GET":
        print 'score'
        return 'dope'

@app.route('/browser_action/', methods=['POST','GET'])
def handle_brower_action():
    error = None
    if request.method == 'POST':
        print request.form["time"]
        socketIO.emit('google_search',dumps({"q":"YEAH!!"}))
        return 'ok'
    if request.method == "GET":
        return 'dope'

if __name__ == "__main__":
    app.debug=True
    app.run(
        host="0.0.0.0",
        port=(5000))