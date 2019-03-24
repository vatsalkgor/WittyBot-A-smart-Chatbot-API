import os, hashlib, aiml, json, time
from flask import Flask, url_for, render_template, request, redirect, session, make_response,flash
from flask_pymongo import PyMongo,ObjectId
from werkzeug.utils import secure_filename
import helpers as h

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['MONGO_URI'] = "mongodb://vatsal_new:vatsal123@ds161335.mlab.com:61335/wittybot"
    app.config['UPLOAD_TEXT'] = "uploads/textfiles/"
    app.secret_key="!@#sdfjgh"
    mongo = PyMongo(app)
    user = mongo.db.wittybot_users
    active_bots = {}
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
            bots = user.find_one({"_id":ObjectId(session['uoid'])},{"chatbots":1,"_id":0})
            return render_template('dashboard.html.j2',bots=bots,name=session['username'])
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
            bots = user.find_one({"_id":ObjectId(session['uoid'])},{"chatbots":1,"_id":0})
            print(type(bots['chatbots']))
            return render_template('mybots.html.j2', bots=bots,name=session['username'])
        return redirect('/')

    @app.route('/createbot')
    def createbot():
        if 'username' in session:
            return render_template('createbot.html.j2',name=session['username'])
        return redirect('/')

    @app.route('/chatbot/<key>')
    def chatbot(key):
        bot_kernel = aiml.Kernel()
        if  os.path.isfile("uploads/brn/"+key+".brn"):
            bot_kernel.bootstrap(brainFile="uploads/brn/"+key+".brn")
            if key not in active_bots:
                active_bots[key] = bot_kernel
        else:
            bot_kernel.bootstrap(learnFiles = "uploads/startups/"+key+"-startup.xml", commands = "load aiml b");
            bot_kernel.saveBrain("uploads/brn/"+key+".brn")
            if key not in active_bots:
                active_bots[key] = bot_kernel
        return render_template('chatbot.html.j2',key=key)

    @app.route('/chatbot/respond',methods=["POST"])
    def respond():
        if request.method=="POST":
            response = active_bots[request.form['key']].respond(request.form['query'])
            if response == '':
                chat_history = {"request_ip":request.form['ip'],"query":request.form['query'],"timestamp":time.time(),"status":0,"response":"Currently I do not know that."}
                user.update_one({"_id":ObjectId(session['uoid']),"chatbots.api_key":request.form['key']},{"$push":{"chat_history":chat_history}})
                return json.dumps(chat_history)
            else:
                chat_history = {"request_ip":request.form['ip'],"query":request.form['query'],"status":1,"timestamp":time.time(),"response":response}
                user.update_one({"_id":ObjectId(session['uoid']),"chatbots.api_key":request.form['key']},{"$push":{"chatbots.$.chat_history":chat_history}})
                return json.dumps(chat_history)

    @app.route('/register',methods=["GET","POST"])
    def register():
        if request.method == "POST":
            if user.find_one({"email":request.form['email']}) is None:
                if user.find_one({'username':request.form['username']}) is None:
                    if request.form['password'] == request.form['cpass']:
                        hash_pass = hashlib.md5(request.form['password'].encode()).hexdigest()
                        user_details = {"username":request.form['username'],
                                        "password":hash_pass,
                                        "email":request.form['email'],
                                        "chatbots":[]}
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

    @app.route("/createBot",methods=["POST"])
    def createBot():
        if request.method=="POST":
            print(request.form)
            print(request.files)
            if 'question_file' in request.files and 'answer_file' in request.files:
                api_key = session['uoid'] + hashlib.md5(request.form['bot_name'].encode()).hexdigest()

                qf = request.files['question_file']
                qf_filename = secure_filename(api_key + "q.txt")
                print(os.path.join(app.config["UPLOAD_TEXT"],qf_filename))
                print(os.getcwd())
                print(qf_filename)
                qf.save(app.config['UPLOAD_TEXT'] + qf_filename)
                
                af = request.files['answer_file']
                af_filename = secure_filename(api_key + "a.txt")
                af.save(app.config['UPLOAD_TEXT'] + af_filename)
                
                questionfile = open(app.config["UPLOAD_TEXT"] + qf_filename)
                answerfile = open(app.config["UPLOAD_TEXT"] + af_filename)
                
                isAIMLgenerated = h.generateAIML(questionfile,answerfile,api_key)
                if isAIMLgenerated:
                    isXMLgenerated = h.generateStartup(api_key)

                chatbot_new = {
                    "bot_name":request.form['bot_name'],
                    "bot_desc":request.form['desc'],
                    "api_key":api_key,
                    "chat_history":[]
                }
                user.update_one({"_id":ObjectId(session['uoid'])},
                            {"$push":{"chatbots":chatbot_new}})
                flash("Bot " + request.form['bot_name'] + " created. ")
                return redirect("mybots")
            else:
                return "no files"
        else:
            return "no post"

    return app