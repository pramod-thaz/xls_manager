import sys

from flask import Flask, render_template, session
from flask_cors import CORS
from user_auth import user_auth,requires_auth
from multiprocessing import Process, freeze_support, Manager

import json
import constants
import config
import asyncio
import websockets

from flaskwebgui import FlaskUI

from path_resolver import resolve

app = Flask(__name__, template_folder=resolve('templates'), static_folder=resolve('static'))


app.secret_key = constants.SECRET_KEY
ui = FlaskUI(app, port=5002, host="localhost")

app.register_blueprint(user_auth, url_prefix='/auth')

## Custom services import
from services.xlsx.extract import extractor
from services.sfr.xlbroker import xlbroker
from services.pbi.app import pbi
from services.analytics.life_expectancy import life_expectancy
import services.sfr.xls_files as xlsf
import xlwings as xw

## Load Config App 
app.config.from_object('services.pbi.config.BaseConfig')

## Register Services here
app.register_blueprint(extractor, url_prefix='/xlsx')
app.register_blueprint(xlbroker, url_prefix='/sfr')
app.register_blueprint(pbi, url_prefix='/pbi')
app.register_blueprint(life_expectancy, url_prefix='/life_expectancy')

from datetime import datetime

CORS(app)

@app.route('/')
@requires_auth
def index():
    if session.get(constants.JWT_PAYLOAD):
        config.USER_INFO = session[constants.JWT_PAYLOAD]    
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    return render_template('index.html', ts=timestamp)

@app.route('/user_info')
def user_info():
    return json.dumps(config.USER_INFO, indent=4)
    
def start_ws(files,xlapp):
    xlsf.files = files
    xlsf.xlapp = xlapp
    start_server = websockets.serve(listen_ws, "localhost", 5003)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


def run_app(files,xlapp):
    xlsf.files = files
    xlsf.xlapp = xlapp
    ui.run()

async def listen_ws(websocket, path):
    await websocket.wait_closed()
    if xlsf.xlapp['pid'] is not None:
        xlapp = xw.apps(xlsf.xlapp['pid'])
        book1 = None
        # uncomment if you want to save books
        # if len(xlapp.books) > 0:
        #     for book in xlapp.books:
        #         if book.name in xlsf.files:
        #             book.save()
        #             book.close()
                    
        xlapp.quit()
           

    sys.exit(0)



if __name__ == "__main__":
    xl_app = {'pid': None}
    xlsf.set_xlapp(xl_app)
    with Manager() as manager:
        files = manager.list(range(0))
        xlapp = manager.dict()
        xlapp['pid'] = xl_app['pid']
        freeze_support()
        a = Process(target=run_app, args=(files,xlapp,))
        a.daemon = True
        a.start()

        c = Process(target=start_ws, args=(files,xlapp,))
        c.start()
        c.join()

    