import time

from flask import Flask

import whigo

app = Flask(__name__)

whigo.wrap_flask_app(app, 'test-flask-app')

def yolo():
    time.sleep(3)

@app.route('/')
def hello_world():
    yolo()
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(port=9199)