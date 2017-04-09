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

def make_absolute(path):
    """returns absolute file path relative to root directory"""
    return os.path.join(app.root_path, path)

def file_upload_location(filename):
    return os.path.join(app.config['VIDEO_UPLOAD_DIR'], filename)

def probe_video(filename):
    """pull relevant information out of ffprobe output"""
    audio, video = ffprobe(filename)
    assert len(video) == 1 and len(audio) <= 1 # exactly one stream
    v = video[0]
    return dict(width=v['width'],
                height=v['height'],
                creation_time=v['tags'].get('creation_time', None))

def fix_wikilink(wikilink):
    if not wikilink or wikilink == "":
        return None

    if not wikilink.startswith("http://metalab.at/wiki/")\
       and not wikilink.startswith("https://metalab.at/wiki/"):
        return "https://metalab.at/wiki/" + wikilink

    return wikilink

def add_video(title, file_path, description, wikilink, creation_time, youtube_id):
    query_db("""INSERT INTO videos(
        title, path, description, wikilink, youtube_id, creation_ts, upload_ts
    ) VALUES(?, ?, ?, ?, ?, strftime('%s',?), strftime('%s','now'))""",
    (title, file_path, description, wikilink, youtube_id, creation_time))

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
    file_path = file_upload_location(file.filename) # this goes into the database
    file_abs_path = make_absolute(file_path) # this is used for actually accessing the file
    file.save(file_abs_path)

    title = request.form.get("title", "")
    description = request.form.get("description", "")
    wikilink = fix_wikilink(request.form.get("wikilink", ""))
    videodata = probe_video(file_abs_path)
    creation_time = videodata['creation_time']
    youtube_id = youtube_upload(file_abs_path, title, description, creation_time)
    add_video(title, file_path, description, wikilink, creation_time, youtube_id)

    return "OK: %s" % youtube_id, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route("/")
def upload_page():
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)
