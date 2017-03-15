import sqlite3
from pprint import saferepr as p
from flask import Flask, g
app = Flask(__name__)

DATABASE="/home/mw/src/ati2/ati.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
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
def hello():
    a=query_db("""INSERT INTO videos(title, path, description, wikilink, timestamp)
    VALUES(?,?,'yolo','yolo',42)""", args=(1,2))
    b=query_db("SELECT * FROM videos")
    get_db().commit()
    return "a: %s\nb:%s" % (p(a), p(b))

if __name__ == "__main__":
    app.run()
