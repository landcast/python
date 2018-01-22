#!/usr/bin/env python

from sanic import Sanic
from sanic import response
import json


app = Sanic()
app.static('/static', './static')
app.static('/favicon.ico', './static/favicon.ico')


@app.route("/")
async def test(request):
    return response.json({"hello": "world"})


@app.post("/json/echo")
async def json_echo(request):
    str_1 = request.body.decode()
    print(str_1)
    param_json = json.loads(str_1)
    return response.json(json.dumps(param_json))


@app.route("/show_upload")
async def show_upload(request):
    return response.html('<html></html>')


@app.route("/upload")
async def upload_file(request):
    '''for single file upload
    '''
    param_file = request.files.get('upload_file')
    file_params = {
        'body': param_file.body,
        'name': param_file.name,
        'type': param_file.type
    }
    return json({'received': True, 'file_names': request.files.keys(), 'file_parameters': file_params})


@app.route("/tag/<tag>")
async def tag_handler(request, tag):
    return response.text('Tag -> {}'.format(tag) + '\n')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
