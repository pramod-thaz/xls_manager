from flask import Blueprint, render_template, jsonify, request
import json 
import re
from datetime import datetime
import services.sfr.xls_manager as XlsManager


xlbroker = Blueprint('xlbroker', __name__, template_folder='templates')

@xlbroker.route('/config')
# read config file and return json to the client!
def get_config():
    file_path = request.args.get('file')
    data = XlsManager.getConfig(file_path)
    return jsonify(data)


@xlbroker.route('/inputs', methods=['POST'])
def inputs():
    file_path = request.args.get('file')
    control = request.args.get('control')
    instance = request.args.get('instance')
    data = json.loads(request.data.decode( 'utf-8' ))
    data = XlsManager.getInputs(file_path, control, instance, data)
    return jsonify(data)



@xlbroker.route('/calculate', methods=['POST'])
def calculate():
    file_path = request.args.get('file')
    data = json.loads(request.data.decode( 'utf-8' ))
    XlsManager.calculate(file_path, data)      
    return {'success': True}




@xlbroker.route('/outputs', methods=['POST'])
def outputs():
    file_path = request.args.get('file')
    control = request.args.get('control')
    instance = request.args.get('instance')
    data = json.loads(request.data.decode( 'utf-8' ))
    data = XlsManager.getOutputs(file_path, control, instance, data)
    return jsonify(data)


@xlbroker.route('/db/names', methods=['GET'])
def db_names():
    control = request.args.get('control')
    file_path = request.args.get('file')
    # get instance names 
    names = XlsManager.getInsNames(control, file_path)
    return jsonify(names)


@xlbroker.route('/db/add', methods=['POST'])
def db_add():
    control = request.args.get('control')
    file_path = request.args.get('file')
    data = json.loads(request.data.decode( 'utf-8' ))
    # TODO check if id exists 
    result = XlsManager.addIns(control,file_path,data['name'])
    return result
    


@xlbroker.route('/db/save', methods=['POST'])
def db_save():
    control = request.args.get('control')
    file_path = request.args.get('file')
    instance = request.args.get('instance')
    data = json.loads(request.data.decode( 'utf-8' ))
    XlsManager.saveIns(control, file_path, instance, data)
    return {'success': True}
    







