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

#THIS IS THE USER FROM GET-IT-DONE; ADDED 10/12
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(20))
    tasks = db.relationship('Task', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

#THIS IS THE USER-VERIFICATION FROM GET-IT-DONE; ADDED 10/12
@app.before_request
def require_login():
  allowed_routs = ['login', 'register']
  if request.endpoingt not in allowed_routs and 'email' not in session:
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
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

#THIS IS THE LOGIN FROM GET-IT-DONE; ADDED 10/12
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
            return redirect('/register')

    return render_template('register.html')

#LOGOUT FROM GET-IT-DONE 10-12
@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

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

#DELETE ENTRY (TASK) FROM GET-IT-DONE 10-12
@app.route('/delete-task', methods=['POST'])
def delete_task():
    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run()