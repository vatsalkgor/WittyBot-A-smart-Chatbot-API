import os
import hashlib
from flask import Flask, url_for, render_template, request, redirect, session, make_response,flash
from flask_pymongo import PyMongo

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['MONGO_URI'] = "mongodb://vatsal_new:vatsal123@ds161335.mlab.com:61335/wittybot"
    app.secret_key="!@#sdfjgh"
    mongo = PyMongo(app)
    user = mongo.db.wittybot_users
    # print((len(user)))
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        if 'username' in session:
            return redirect('/dashboard')
        else:
            return render_template('login.html.j2')

    # @app.route('/login')
    # def login():
    #     return 'login'

    # @app.route('/user/<username>')
    # def profile(username):
    #     return '{}\'s profile'.format(username)

    # with app.test_request_context():
    #     print(url_for('index'))
    #     # print(url_for('login'))
    #     # print(url_for('login', next='/'))
    #     print(url_for('profile', username='John Doe'))

    # @app.context_processor
    # def example():
    #     return dict(myexample="this is my example")

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            if 'username' in session:
                return redirect('/dashboard')
            else:
            # login logic -- in future will be replaced with database login logic. 
                hashed_pass = hashlib.md5(request.form['password'].encode()).hexdigest()
                if user.find_one({"username":request.form['username'],"password":hashed_pass}) is not None:
                    session['username'] = request.form['username'];
                    session['uoid'] = str(user.find_one({"username":request.form['username']})['_id'])
                    return redirect('dashboard')
                else:
                    return render_template('login.html.j2',error_msg='Username or password is incorrect.')
        else:
            return render_template("login.html.j2")

    @app.route('/dashboard')
    def dashboard():
        if 'username' in session:
            # get the all created bots by user and send it to the dashboard

            return render_template('dashboard.html.j2',bots=None,name=session['username'])
        else:
            return redirect('/')

    @app.route('/logout')
    def logout():
        # remove session here and then call login again
        session.clear()
        return redirect('/')

    @app.route('/mybots')
    def mybots():
        if 'username' in session:
            # get the all created bots by user and send it to the dashboard
            return render_template('mybots.html.j2', bots=None)
        return redirect('/')

    @app.route('/createbot')
    def createbot():
        if 'username' in session:
            return render_template('createbot.html.j2')
        return redirect('/')

    @app.route('/chatbot')
    def chatbot():
        if 'username' in session:
            return render_template('chatbot.html.j2')
        return redirect('/')
        
    @app.route('/register',methods=["GET","POST"])
    def register():
        if request.method == "POST":
            if user.find_one({"email":request.form['email']}) is None:
                if user.find_one({'username':request.form['username']}) is None:
                    if request.form['password'] == request.form['cpass']:
                        hash_pass = hashlib.md5(request.form['password'].encode()).hexdigest()
                        user_details = {"username":request.form['username'],
                                        "password":hash_pass,
                                        "email":request.form['email']}
                        user.insert_one(user_details)
                        flash("Successfully registered.")
                        return redirect(url_for("login"))
                    else:
                        return render_template('register.html.j2',fail_msg="Password and Confirm Password does not match")
                else:
                    return render_template("register.html.j2",fail_msg="Choose a different username. ")
            else:
                return render_template("register.html.j2",fail_msg="User already registered.")
        else:
            return render_template('register.html.j2')

    return app