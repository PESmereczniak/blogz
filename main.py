from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    def __init__(self, blog_title, blog_text, owner):
        self.blog_title = blog_title
        self.blog_text = blog_text
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
  allowed_routs = ['login', 'register', 'blog', 'index']
  if request.endpoint not in allowed_routs and 'email' not in session:
    return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged In")
            return redirect('/userblog')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html', title="Account Login")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        if len(password) <= 2 or len(password) >= 21 or ' ' in password:
            flash('Password must be at least three (3) characters long and CANNOT contain spaces.', 'error')
            return render_template('register.html', email=email)

        if password != verify:
            flash('Passwords MUST match.  Please re-enter.', 'error')
            return render_template('register.html', email=email)

        existing_user = User.query.filter_by(email=email).first()

        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/newpost')
        else:
            flash('User name already exists', 'error')
            return redirect('/login')

    return render_template('register.html', title="Register New Account")

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def make_newpost():
    return render_template('newpost.html', title="Create New Post")

@app.route('/submitnew', methods=['POST', 'GET'])
def submitnew():
    blog_title = request.form['blog_title']
    blog_text = request.form['blog_text']
    blogs = Blog.query.all()
    owner = User.query.filter_by(email=session['email']).first()

    if blog_title == '':
        flash("Title required to post!", 'error')
        return render_template('newpost.html', title="Blog",blogs=blogs,blog_text=blog_text)
    
    if blog_text == '':
        flash("Body required to post", 'error')
        return render_template('newpost.html', title="Blog",blogs=blogs,blog_title=blog_title)

    if request.method == 'POST':
        newpost = Blog(blog_title, blog_text, owner)
        db.session.add(newpost)
        db.session.commit()

    thisblog = newpost
    return render_template('indblog.html',title=thisblog.blog_title,thisblog=thisblog)

#THIS CALLS ALL BLOG ENTRIES FROM ALL USERS
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('name')
    theuser = request.args.get('id')
    blogs = Blog.query.all()

    if blog_id:
        thisblog = Blog.query.get(blog_id)
        return render_template('indblog.html',title=thisblog.blog_title,thisblog=thisblog)

    if theuser: #FOR SHOWING LIST OF ONE USER'S BLOG ENTRIES
        user = User.query.filter_by(email=theuser).all()
        return render_template('userblog.html',user=user,blogs=blogs)

    else: #LISTS ALL BLOG ENTRIES BY ALL USERS
        return render_template('blog.html',title="Blog",blogs=blogs)

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/userblog', methods=['POST', 'GET'])
def user_index():
    owner = User.query.filter_by(email=session['email']).first()
    blogs = Blog.query.filter_by(owner=owner).all()

    return render_template('blog.html',title="My Blogs", blogs=blogs, owner=owner)

#THIS WILL RENDER A PAGE OF ALL CONTRIBUTERS, THEIR NAME/EMAIL WILL LINK TO THEIR HOME PAGE
@app.route('/users', methods=['POST', 'GET'])


#DELETE ENTRY (TASK) FROM GET-IT-DONE 10-12
#DELETING ENTRY FAILS ALL CHECKS - WILL NOT DELETE; WILL NOT REROUTE/RENDER, ETC
@app.route('/deleteblog', methods=['POST', 'GET'])
def delete_blog():
    thisblog = Blog.query.get(blog_id)
    blogs = Blog.query.all()
    owner = User.query.filter_by(email=session['email']).first()

    if Blog.owner_id == User.id:
        #thisblog = Blog.query.get(Blog.id)
        db.session.add(blog)
        db.session.commit()
        flash("Blog Entry Deleted!", 'error')
    else:
      flash("You do not have permission to DELETE that blog", 'error')
      
    return render_template('blog.html', blogs=blogs, owner=owner)

if __name__ == '__main__':
    app.run()