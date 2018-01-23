#!/usr/bin/env python

from sanic import Sanic
from sanic import response
from config import appconfig
import os
import json
import base64


app = Sanic('l1-1')


def init(app):
    ''' sanic app init process, the load priority controled by loading sequence
    '''
    # try to load UPLOAD_LOCATION
    try:
        print("from env variable", app.config.UPLOAD_LOCATION)
    except:
        print("not found in env for SANIC_UPLOAD_LOCATION")

    # test config load priority, env variable -> object -> config file
    app.config.from_object(appconfig())

    try:
        print("check APP_CONFIG_FILE from os", os.environ['APP_CONFIG_FILE'])
    except:
        print("check APP_CONFIG_FILE, but not exist")
    else:
        app.config.from_envvar('APP_CONFIG_FILE')
        print("from envvar load config file", app.config.UPLOAD_LOCATION)

    app.config.UPLOAD_LOCATION = '/var/upload/l1-1'
    print("set newlocation", app.config.UPLOAD_LOCATION)

    print("load upload_location from object", app.config.UPLOAD_LOCATION)
    app.static('/static', './static')
    app.static('/favicon.ico', './static/favicon.ico', name='favicon.ico')


@app.route("/")
async def test(request):
    return response.json({"hello": "world"})


@app.post("/json/echo")
async def json_echo(request):
    param_json = json.loads(request.body.decode())
    param_json['id'] = param_json['id'] + 1
    return response.json(json.dumps(param_json))


@app.post("/form")
async def upload_file(request):
    '''form demo
    '''
    for key in request.form:
        param = request.form.get(key)
        print(key, param)
    return response.json({'received': True, 'form': request.form})


@app.route("/show_upload")
async def show_upload(request):
    return response.html('<html></html>')


@app.post("/upload")
async def upload_file(request):
    '''for single file upload
    '''
    file_params = list()
    for key in request.files:
        param_file = request.files.get(key)
        print(key)
        # b64str = base64.b64encode(param_file.body)
        file_params.append({
            # 'body': b64str,
            'name': param_file.name,
            'type': param_file.type
        })
    return response.json({'received': True, 'file_names': request.files.keys(), 'file_params': file_params})


@app.route("/tag/<tag>")
async def tag_handler(request, tag):
    return response.text('Tag -> {}'.format(tag) + '\n')


if __name__ == "__main__":
    init(app)
    app.run(host="0.0.0.0", port=8080, workers=2)
