import os

from flask import Flask, url_for, render_template, request, redirect


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
        return render_template('login.html')

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


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            # login logic -- in future will be replaced with database login logic. 
            if request.form['username'] == "vatsal" and request.form['password'] == "vatsal@223":
                return redirect('dashboard')
            else:
                return render_template('login.html',error_msg='Username or password is incorrect.')
        else:
            return redirect('/login')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/logout')
    def logout():
        # remove session here and then call login again
        return redirect('/')

    return app