#!/usr/bin/env python

from sanic import Sanic
from sanic import response
import json
import base64


app = Sanic('l1-1')
app.static('/static', './static')
app.static('/favicon.ico', './static/favicon.ico', name='favicon.ico')
app.config.upload_location = '/var/upload/l1-1'


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
    app.run(host="0.0.0.0", port=8080, workers=2)
