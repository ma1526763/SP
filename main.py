from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime
import os

app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = os.environ['S_KEY']
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
db.create_all()

# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

# invalid strip bleach
# def strip_invalid_html(content):
#     allowed_tags = ['a', 'abbr', 'acronym', 'address', 'b', 'br', 'div', 'dl', 'dt',
#                     'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
#                     'li', 'ol', 'p', 'pre', 'q', 's', 'small', 'strike',
#                     'span', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
#                     'thead', 'tr', 'tt', 'u', 'ul']
#     allowed_attrs = {
#         'a': ['href', 'target', 'title'],
#         'img': ['src', 'alt', 'width', 'height'],
#     }
#     cleaned = bleach.clean(content,
#                            tags=allowed_tags,
#                            attributes=allowed_attrs,
#                            strip=True)
#     return cleaned

posts = BlogPost.query.all()
@app.route('/')
def get_all_posts():
    return render_template("index.html", all_posts=posts)
@app.route("/post/<int:index>")
def show_post(index):
    requested_post = posts[index-1]
    return render_template("post.html", post=requested_post)
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/edit_post", methods=["GET", "POST"])
def edit_post():
    post_id = request.values['post_id']
    if request.method == "GET":
        post = BlogPost.query.get(post_id)
        form = CreatePostForm(title=post.title, subtitle=post.subtitle, img_url=post.img_url, author=post.author, body=post.body)
        return render_template('make-post.html', form=form, is_edit=True, post_id=post_id)
    if request.method == "POST":
        form = CreatePostForm()
        if form.validate_on_submit():
            blog_post = BlogPost.query.get(post_id)
            blog_post.title = request.values['title']
            blog_post.subtitle = request.values['subtitle']
            blog_post.img_url = request.values['img_url']
            blog_post.author = request.values['author']
            blog_post.body = request.values['body']
            db.session.commit()
            return redirect(url_for("show_post", index=post_id))
        return redirect(url_for('edit_post', post_id=post_id))

@app.route("/new_post", methods=["GET", "POST"])
def create_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_blog = BlogPost(
            title=request.values['title'],
            subtitle=request.values['subtitle'],
            author=request.values['author'],
            img_url=request.values['img_url'],
            body=request.values['body'],
            date=datetime.now().strftime("%B %d, %Y")
        )
        db.session.add(new_blog)
        db.session.commit()

        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form, is_edit=False)

@app.route("/delete")
def delete_post():
    post = BlogPost.query.get(request.values['post_id'])
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)