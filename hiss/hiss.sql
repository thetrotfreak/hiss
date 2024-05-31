-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS likes;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  body TEXT CHECK(LENGTH(body) <= 150) NOT NULL,
  reply_to_id INTEGER,
  FOREIGN KEY (author_id) REFERENCES user (id),
  FOREIGN KEY (reply_to_id) REFERENCES post (id),
  CHECK (reply_to_id IS NULL OR reply_to_id != id)
);

CREATE TABLE likes (
  post_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  PRIMARY KEY (post_id, user_id),
  FOREIGN KEY (post_id) REFERENCES post (id),
  FOREIGN KEY (post_id) REFERENCES user (id)
)