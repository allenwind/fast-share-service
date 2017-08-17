import os
import base64
import argparse

from flask import (Flask, redirect, url_for,
    request, send_file, flash)
from gevent.wsgi import WSGIServer

flash = print

HTML_TEMPLATE = \
'''
<!DOCTYPE html>
    <title>File Service</title>
        <h2>file list</h2>
        {}
        <br>
        <h2>upload file</h2>
        <form method=post enctype=multipart/form-data>
            <p><input type=file name=file>
               <input type=submit value=upload>
        </form>
</html>
'''

class Config(object):
    DEBUG = False
    UPLOAD_FOLDER = './uploads'


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.use_x_sendfile = False
    return app

app = create_app(Config)

@app.before_first_request
def init():
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.mkdir(app.config["UPLOAD_FOLDER"])

@app.route('/', methods=['GET'])
def list_files():
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    r = []
    for file in files:
        item = '<li><a href="/file?path={}">{}</a></li>'.format(base64.b64encode(file.encode('utf-8')).decode('utf-8'), file)
        r.append(item)
    return HTML_TEMPLATE.format('\n'.join(r))

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('not file part')
        return redirect(url_for('list_files'))
    file = request.files['file']
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        flash('file uploading is ok!')
    return redirect(url_for('list_files'))

@app.route('/file')
def download():
    path = request.args.get("path", default=None)
    if path is None:
        return redirect(url_for('list_files'))
    filename = base64.b64decode(path.encode('utf-8')).decode('utf-8')
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        fp = open(path, 'rb')
        return send_file(fp, mimetype='application/octet-stream', as_attachment=True,
                         attachment_filename=filename)
    else:
        flash("file not found")
        return redirect(url_for('list_files'))

@app.after_request
def add_headers(response):
    response.headers['Server'] = 'File Service/1.0'
    return response

def start_app(address, app=app):
    server = WSGIServer(address, app)
    server.serve_forever()

if __name__ == '__main__':
    '''
    parser = argparse.ArgumentParser(description='file service for human')
    parser.add_argument('-p', type=int)
    parser.add_argument('--host')
    parser.parse_args()
    host = parser.host if parser.h is not None else '0.0.0.0'
    port = parser.p if parser.p is not None else 8080
    '''
    host = '0.0.0.0'
    port = 8080
    address = (host, port)
    start_app(address)
