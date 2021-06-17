import xlwings as xw

# init xls app
def set_xlapp(xlapp):
    if xlapp['pid'] is None:
        xl_app = xw.App(visible=False)#,add_book=False)
        xlapp['pid'] = xl_app.pid

files = []
xlapp = {'pid': None}