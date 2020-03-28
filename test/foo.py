from flask import Flask

from whigo import wrap_flask_app

app = Flask(__name__)

wrap_flask_app(app, 'test-flask-app')


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run()
