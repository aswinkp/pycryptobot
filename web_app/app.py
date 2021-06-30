from functools import wraps

from flask import Flask, render_template, request, redirect
import json

app = Flask(__name__)


def login_required(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        auth = request.authorization
        if not (auth and auth.username=='admin@123' and auth.password=="pass@w0rd"):
            return ('Unauthorized', 401, {
                'WWW-Authenticate': 'Basic realm="Login Required"'
            })

        return f(**kwargs)

    return wrapped_view


@app.route("/")
@login_required
def home():
    f = open('../running.json')
    data = json.load(f)
    f.close()
    return render_template("base.html", data=data['names'])



@app.route('/sampledata')
@login_required
def sampleData():
    f = open('../running.json')
    data = json.load(f)
    return data

@app.route('/sell', methods=['POST'])
@login_required
def updateData():
    key = request.form.get("key")
    f = open('../running.json')
    data = json.load(f)
    f.close()
    data['names'][key]['should_sell'] = True
    with open("../running.json", "w") as outfile:
        json.dump(data, outfile,indent=4)
    return redirect('/')

@app.after_request
def apply_caching(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response