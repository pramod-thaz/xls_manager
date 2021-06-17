from flask import current_app as app
import xlwings as xw
from datetime import datetime
import re
from xlwings.constants import DeleteShiftDirection
import ntpath
import services.sfr.xls_files as xlsf
from tinydb import TinyDB, Query


db = TinyDB('data/xlbroker_db.json')


def fileName(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def getBook(file):
    with app.app_context():    
        try:
            book= xw.apps(xlsf.xlapp['pid']).books[fileName(file)]
        # in case you add add_book=False on init
        # except AttributeError: 
        #     book= xw.Book(file)
        #     pass
        except KeyError:
            book= xw.apps(xlsf.xlapp['pid']).books.open(file)
            xlsf.files.append(fileName(file))
            pass
        return book

def getConfig(file):
    sht = getBook(file).sheets['Config']
    header = sht.range('A1:J1').value 
    table = sht.range('A2:J100').value 
    data = []
    for row in table:
        obj = {}
        obj_nil = True
        for i in range(len(row)-1):
            if row[i] is not None: 
                obj_nil = False
            if header[i] is not None:
                obj[header[i]] = row[i]
        if obj_nil:
            break    
        data.append(obj)
        
    return data


def getXlsInputs(file, data):
    for attr in data:
        if attr['Sheet'] is not None and attr['Range'] is not None:
            sht = getBook(file).sheets[attr['Sheet']]
            if attr['Type'] == 'table':
                attr['Value'] = sht.used_range.value
            else:
                val = sht.range(attr['Range']).value
                attr['Value'] = getJsonValue(val) 

    return data


def getDbInputs(file, control, instance, data):
    db_file = Query()
    db_data = db.search(db_file.inputfile == file and db_file.control == control and db_file.instance == instance)
    if len(db_data) > 0 and db_data[0].get('inputs') is not None:
        return db_data[0]['inputs']
    return getXlsInputs(file, data)


def getInputs(file, control, instance, data):
    # if instance is default load from xls
    if instance == 'default':
        return  getXlsInputs(file, data)
    
    return getDbInputs(file, control, instance, data)

def calculate(file,data):
    for attr in data:
        if attr['Sheet'] is not None and attr['Range'] is not None:
            sht = getBook(file).sheets[attr['Sheet']]

            if attr['Type'] == 'variant' and len(attr['Value']) == 1:
                attr['Value'] = attr['Value'][0]

            if attr['Type'] == 'table':
                # doesn't update if data is empty
                if attr['Value']:
                    try:
                        sht.range('2:10000').api.Delete(DeleteShiftDirection.xlShiftUp)
                    except:
                        pass
                    sht.range(attr['Range']).options(expand='table', index=False).value = processTable(attr['Value'])
            else:
                sht.range(attr['Range']).value = attr['Value']


def getXlsOutputs(file, data):
    for attr in data:
        if attr['Sheet'] is not None and attr['Range'] is not None:
            sht = getBook(file).sheets[attr['Sheet']]
            val = sht.range(attr['Range']).value
            attr['Value'] = getJsonValue(val) if val is not None else ''
    return data

def getDbOutputs(file, control, instance, data):
    db_file = Query()
    db_data = db.search(db_file.inputfile == file and db_file.control == control and db_file.instance == instance)
    if len(db_data) > 0 and db_data[0].get('outputs') is not None:
        return db_data[0]['outputs']
    return getXlsOutputs(file, data)


def getOutputs(file, control, instance, data):
    if instance == 'default':
        return getXlsOutputs(file, data)

    return getDbOutputs(file, control, instance, data)


def getInsNames(control,filename):
    db_file = Query()
    data = db.search(db_file.inputfile == filename and db_file.control == control)
    names = []
    for ins in data:
        names.append(ins['instance'])
    return names


def addIns(control,filename,name):
    if name == 'default':
        return {'success': False, 'message': 'Reserved Name'}
    db_file = Query()
    data = db.search(db_file.inputfile == filename and db_file.control == control and db_file.instance == name)
    if len(data) == 0:
        db.insert({'inputfile': filename, 'instance': name, 'control': control})
        return {'success': True}
    else:
        return {'success': False, 'message': 'Name already exist'}



def saveIns(control,filename,instance,data):
    db_file = Query()
    data['inputfile'] = filename
    data['control'] = control
    data['instance'] = instance
    db.upsert(data, db_file.inputfile == filename and db_file.control == control and db_file.instance == instance)



def jsonRow(row):
    ctab = []
    for cell in row:
        ctab.append(str(cell) if cell is not None else '')

    return ctab

def getJsonValue(val):
    if isinstance(val,list):
        tab = []
        for cell in val:
            if isinstance(cell,list):
                row = jsonRow(cell)
                tab.append(row)
            else:
                tab.append(str(cell) if cell is not None else '')

        return tab

    return str(val)


## this will format value, for now it's just date value
def processTable(table):
    table = table[1:]
    ntab = []
    for row in table:
        rval = []
        for cell in row:
            rval.append(format(cell))
        ntab.append(rval)
    return ntab

#just format simple date 
def format(val):
    if val is None:
        return ''
    if isinstance(val, str) and  re.search("\d+\/\d+\/\d+",val):
        val = datetime.strptime(val, '%m/%d/%Y')

    return str(val)