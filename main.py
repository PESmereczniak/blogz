from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
#pylint: disable=no-member

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:rehcr1943@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '123456abcdef'

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True) 
    blog_title = db.Column(db.String(60))
    blog_text = db.Column(db.String(1000))

    def __init__(self, blog_title, blog_text):
        self.blog_title = blog_title
        self.blog_text = blog_text

@app.route('/newpost', methods=['POST', 'GET'])
def make_newpost():
    return render_template('newpost.html', title="Create New Post")

@app.route('/submitnew', methods=['POST', 'GET'])
def submitnew():
    blog_title = request.form['blog_title']
    blog_text = request.form['blog_text']
    blogs = Blog.query.all()

    if blog_title == '':
        flash("Title required to post!", 'error')
        return render_template('newpost.html', title="Blog",blogs=blogs,blog_text=blog_text)
    
    if blog_text == '':
        flash("Body required to post", 'error')
        return render_template('newpost.html', title="Blog",blogs=blogs,blog_title=blog_title)

    if request.method == 'POST':
        newpost = Blog(blog_title, blog_text)
        db.session.add(newpost)
        db.session.commit()

    thisblog = newpost
    return render_template('indblog.html',title=thisblog.blog_title,thisblog=thisblog)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('name')
    if blog_id:
        thisblog = Blog.query.get(blog_id)
        return render_template('indblog.html',title=thisblog.blog_title,thisblog=thisblog)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html',title="Blog",blogs=blogs)

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('base.html',title="Build-a-Blog")

if __name__ == '__main__':
    app.run()