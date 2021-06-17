from services.pbi.aadservice import getaccesstoken
from services.pbi.pbiembedservice import getembedparam
from flask import Blueprint, request, current_app as app
import json
import os
import requests


pbi = Blueprint('pbi', __name__, template_folder='templates')


@pbi.route('/getembedinfo', methods=['GET'])
def getembedinfo():
    '''Returns Embed token and Embed URL'''
    REPORT_ID = request.args.get('REPORTID')
    WORKSPACE_ID = request.args.get('WORKSPACEID')

    configresult = checkconfig()
    if configresult is None:
        try:
            accesstoken = getaccesstoken()
            embedinfo = getembedparam(accesstoken,REPORT_ID,WORKSPACE_ID)
        except Exception as ex:
            return json.dumps({'errorMsg': str(ex)}), 500
    else:
        return json.dumps({'errorMsg': configresult}), 500

    return embedinfo


def checkconfig():
    '''Returns a message to user for a missing configuration'''
    if app.config['AUTHENTICATION_MODE'] == '':
        return 'Please specify one the two authentication modes'
    if app.config['AUTHENTICATION_MODE'].lower() == 'serviceprincipal' and app.config['TENANT_ID'] == '':
        return 'Tenant ID is not provided in the config.py file'
    elif app.config['CLIENT_ID'] == '':
        return 'Client ID is not provided in config.py file'
    elif app.config['AUTHENTICATION_MODE'].lower() == 'masteruser':
        if app.config['POWER_BI_USER'] == '':
            return 'Master account username is not provided in config.py file'
        elif app.config['POWER_BI_PASS'] == '':
            return 'Master account password is not provided in config.py file'
    elif app.config['AUTHENTICATION_MODE'].lower() == 'serviceprincipal':
        if app.config['CLIENT_SECRET'] == '':
            return 'Client secret is not provided in config.py file'
    elif app.config['SCOPE'] == '':
        return 'Scope is not provided in the config.py file'
    elif app.config['AUTHORITY_URL'] == '':
        return 'Authority URL is not provided in the config.py file'
    
    return None