#!/usr/bin/env python


from flask import Flask
from app_log import app_log
from app_issue import app_issue


app = Flask(__name__)
app.register_blueprint(app_log)
app.register_blueprint(app_issue)


if __name__ == '__main__':
    app.run()
