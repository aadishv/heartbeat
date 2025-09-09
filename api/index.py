from flask import Flask, jsonify, request
import traceback
import os
from playhouse.shortcuts import model_to_dict
from locator import locate
import time
from db import Visitor, Visit
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# Read authentication credentials from environment variables
AUTH_USERNAME = os.getenv('AUTH_USERNAME')
AUTH_PASSWORD = os.getenv('AUTH_PASSWORD')

if not AUTH_USERNAME or not AUTH_PASSWORD:
    raise ValueError("AUTH_USERNAME and AUTH_PASSWORD environment variables must be set")

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
    # Check for authentication via query parameters
    username = request.args.get('username')
    password = request.args.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password query parameters are required"}), 401
    
    if username != AUTH_USERNAME or password != AUTH_PASSWORD:
        return jsonify({"error": "Invalid credentials"}), 401
    
    visits = [model_to_dict(v) for v in list(Visit.select())]
    return jsonify(visits)

if __name__ == '__main__':
    app.run()
