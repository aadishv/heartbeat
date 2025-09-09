from flask import Flask, jsonify, request
import traceback
from playhouse.shortcuts import model_to_dict
from locator import locate
import time
from db import Visitor, Visit
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

def handle(ip: str, path: str):
    """
    extracted out so we can use this for testing
    path is something like "/tools/periodic"
    """
    prev_matches = list(Visitor.select().where(Visitor.ip == ip))
    if prev_matches:
        visitor = prev_matches[0]
    else:
        match = locate(ip)
        visitor = Visitor.create(ip=ip, country=match.country if match else None, lat=match.lat if match else None, long=match.long if match else None)
        visitor.save()
    # we now know the visitor!
    visit = Visit.create(visitor=visitor, timestamp=time.time() * 1000, path=path)
    visit.save()
    # erson(name='Bob', birthday=date(1960, 1, 15))

@app.route('/ping/<path:subpath>')
def ping(subpath):
    try:
        print(subpath)
        ip = request.remote_addr
        handle(ip, subpath)
        return "OK"
    except Exception as e:
        stacktrace = traceback.format_exc()
        return jsonify({"error": str(e), "stacktrace": stacktrace}), 500

@app.route('/ping', strict_slashes=False)
def ping_slash():
    return ping('')

@app.route('/dump')
def dump():
    visits = [model_to_dict(v) for v in list(Visit.select())]
    return jsonify(visits)

if __name__ == '__main__':
    app.run()
