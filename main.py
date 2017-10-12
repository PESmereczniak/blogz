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
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, blog_text, owner):
        self.blog_title = blog_title
        self.blog_text = blog_text
        self.owner = owner

#THIS IS THE USER FROM GET-IT-DONE; ADDED 10/12
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

#THIS IS THE USER-VERIFICATION FROM GET-IT-DONE; ADDED 10/12
@app.before_request
def require_login():
  allowed_routs = ['login', 'register']
  if request.endpoint not in allowed_routs and 'email' not in session:
    return redirect('/login')

#THIS IS THE LOGIN FROM GET-IT-DONE; ADDED 10/12
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

#THIS IS THE REGISTER FROM GET-IT-DONE; ADDED 10/12
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #TODO - validate user's entered DATA - ADDED 10/10/17 - FLASH ERRORS, KEEPS EMAIL
        if len(password) <= 2 or len(password) >= 21 or ' ' in password:
            flash('Password must be at least eight (3) characters long and CANNOT contain spaces.', 'error')
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
            return redirect('/')
        else:
            flash('User name already exists', 'error')
            return redirect('/login')

    return render_template('register.html', title="Register New Account")

#LOGOUT FROM GET-IT-DONE 10-12
@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/newpost', methods=['POST', 'GET'])
def make_newpost():
    return render_template('newpost.html', title="Create New Post")

#USER SUBMIT NEW POST
@app.route('/submitnew', methods=['POST', 'GET'])
def submitnew():
    blog_title = request.form['blog_title']
    blog_text = request.form['blog_text']
    blogs = Blog.query.all()
    owner = User.query.filter_by(email=session['email']).first()
    email = request.args.get('email')

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
    if blog_id:
        thisblog = Blog.query.get(blog_id)
        return render_template('indblog.html',title=thisblog.blog_title,thisblog=thisblog)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html',title="Blog",blogs=blogs)

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('base.html',title="Build-a-Blog")

#THIS WILL BE FOR CALLING THE USER'S BLOG POSTS ONLY
@app.route('/userblog', methods=['POST', 'GET'])
def user_index():
    owner = User.query.filter_by(email=session['email']).first()
    blogs = Blog.query.filter_by(owner=owner).all()

    return render_template('blog.html',title="My Blogs", blogs=blogs, owner=owner)

#DELETE ENTRY (TASK) FROM GET-IT-DONE 10-12
@app.route('/delete-blog', methods=['POST'])
def delete_blog():
    if Blog.owner_id == User.id:
        blog_id = int(request.form['blog_id'])
        blog = Blog.query.get(blog_id)
        db.session.add(blog)
        db.session.commit()
    else:
      flash("You do not have permission to DELETE this blog", 'error')
      return redirect('/blog')

if __name__ == '__main__':
    app.run()