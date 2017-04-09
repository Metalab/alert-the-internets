CREATE TABLE videos(
        id            INTEGER PRIMARY KEY
      , title         TEXT NOT NULL
      , path          TEXT NOT NULL
      , description   TEXT NOT NULL DEFAULT ""
      , wikilink      TEXT
      , youtube_id    TEXT
      , upload_ts     INTEGER
      , creation_ts   INTEGER
);
