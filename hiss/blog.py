from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
import sqlite3

from .auth import login_required
from .db import get_db

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        "SELECT p.id, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    likes = db.execute("SELECT * FROM likes").fetchall()
    return render_template("blog/index.html", posts=posts, likes=likes)


@bp.route("/replies")
def replies():
    """Show all your replies, most recent first."""
    db = get_db()
    replies = db.execute(
        "SELECT p.id, p.body, p.created, p.author_id, u.username"
        " FROM post p"
        " JOIN user u ON p.author_id = u.id"
        " WHERE p.author_id = ? AND p.reply_to_id IS NOT NULL"
        " ORDER BY p.created DESC",
        (g.user["id"],),
    ).fetchall()
    return render_template("blog/reply.all.html", posts=replies)


@bp.route("/likes")
def likes():
    """Show all your likes, most recent first."""
    db = get_db()
    likes = db.execute(
        "SELECT p.*, username"
        " FROM post p"
        " JOIN likes l on p.id = l.post_id"
        " JOIN user u on p.author_id = u.id"
        " WHERE l.user_id = ?"
        " ORDER BY p.created DESC",
        (g.user["id"],),
    ).fetchall()
    return render_template("blog/like.all.html", posts=likes)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, reply_to_id, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        body = request.form["body"]
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO post (body, author_id) VALUES (?, ?)",
                    (body, g.user["id"]),
                )
            except sqlite3.IntegrityError:
                # TODO
                # thrown for check constraint failure
                # blog.body should have atmost 150 characters
                # but, what when requirements change
                # can we get more specific error from sqlite3
                error = "You can only post upto 150 characters"
                flash(error)
            else:
                db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        body = request.form["body"]
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute("UPDATE post SET body = ? WHERE id = ?", (body, id))
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/reply", methods=("GET", "POST"))
@login_required
def reply(id):
    """Reply to a post if the current user is not the author."""
    post = get_post(id=id, check_author=False)

    if request.method == "POST":
        body = request.form["body"]
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT OR REPLACE INTO post (body, author_id, reply_to_id) VALUES (?, ?, ?)",
                (body, g.user["id"], id),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/reply.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))


@bp.route("/<int:post_id>/like", methods=("POST",))
@login_required
def like(post_id):
    """Like/unlike a post.

    Ensures that the post exists and that the logged in user is not the
    author of the post.
    """
    get_post(id=post_id, check_author=False)
    db = get_db()
    try:
        db.execute(
            "INSERT INTO likes (post_id, user_id) VALUES (?, ?)",
            (post_id, g.user["id"]),
        )
    except sqlite3.IntegrityError:
        db.execute(
            "DELETE FROM likes WHERE post_id = ? AND user_id = ?",
            (post_id, g.user["id"]),
        )
    finally:
        db.commit()
    return redirect(url_for("blog.index"))
