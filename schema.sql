CREATE TABLE videos(
        id            INTEGER PRIMARY KEY
      , title         TEXT NOT NULL
      , path          TEXT NOT NULL
      , description   TEXT NOT NULL DEFAULT ""
      , wikilink      TEXT
      , timestamp     INTEGER NOT NULL DEFAULT 0
);
