from flask import Flask

import whigo

app = Flask(__name__)

whigo.wrap_flask_app(app, 'test-flask-app')


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run()
