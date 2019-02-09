import os

from flask import Flask, url_for, render_template, request, redirect, session, make_response


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

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
                if request.form['username'] == "vatsal" and request.form['password'] == "vatsal@223":
                    session['username'] = request.form['username'];
                    return redirect('dashboard')
                else:
                    return render_template('login.html.j2',error_msg='Username or password is incorrect.')
        else:
            return redirect('/login')

    @app.route('/dashboard')
    def dashboard():
        if 'username' in session:
            # get the all created bots by user and send it to the dashboard
            return render_template('dashboard.html.j2',bots=None)
        else:
            return redirect('/')

    @app.route('/logout')
    def logout():
        # remove session here and then call login again
        session.pop('username')
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
        
    @app.route('/register')
    def register():
        return render_template('register.html.j2')
        
    return app