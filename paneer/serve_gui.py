from flask import Flask, send_from_directory
from paneer.comms import exposed_functions
import json
import os
import sys

if getattr(sys, 'frozen', False):
    # Some weird thing when bundled with pyinstaller the bootloader sets path in _MEIPASS
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
    application_path = os.path.dirname(application_path)

print(application_path)
app = Flask(__name__)

directory_to_serve = os.path.join(application_path, 'gui')

@app.route('/')
@app.route('/<path:filename>')
def serve_file(filename='index.html'):
    if filename == '':
        filename = 'index.html'
    return send_from_directory(directory_to_serve, filename)

@app.route('/call/<command>')
def command(command):
    if command in exposed_functions:
        return json.dumps({"res":exposed_functions[command]()})
    return f'no command named: {command}', 404

if __name__ == '__main__':
    app.run(debug=True,port=8765)