#!/usr/bin/env python3
from flask import Flask, g, render_template, request
import sqlite3, os.path, tempfile
from subprocesses import ffprobe, youtube_upload
from pprint import saferepr as p

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('default_settings')
app.config.from_pyfile('ati.conf', silent=True)

tempfile.tempdir = app.config.get('TEMP_DIR', '/tmp')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        dbpath = os.path.join(app.instance_path, app.config['SQLITE_DATABASE'])
        db = g._database = sqlite3.connect(dbpath)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.commit()
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/")
def upload_page():
    return render_template("upload.html")

def file_upload_location(filename):
    return os.path.join(app.root_path, app.config['VIDEO_UPLOAD_DIR'], filename)

def probe_video(filename):
    audio, video = ffprobe(filename)
    assert len(video) == 1 and len(audio) <= 1 # exactly one stream
    v = video[0]
    return dict(width=v['width'],
                height=v['height'],
                creation_time=v['tags'].get('creation_time', None))

@app.route("/upload", methods=["POST"])
def do_upload():
    # check if the post request has the file part
    if 'file' not in request.files:
        return "no file part" # FIXME use a template
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if not file.content_type in app.config['VIDEO_CONTENT_TYPES']:
        return "File not allowed"
    file_path = file_upload_location(file.filename)
    file.save(file_path)
    msg = "File saved as: %s" % file_path
    ytmsg = "Youtube URL: %s" % youtube_upload(file_path, request.form['title'])
    return "\n".join(["OK", msg, ytmsg]), 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == "__main__":
    app.run(debug=True)
