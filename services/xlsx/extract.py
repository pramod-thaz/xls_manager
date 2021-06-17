
from flask import Blueprint, render_template


extractor = Blueprint('extract', __name__, template_folder='templates')

from path_resolver import resolve

import pandas as pd
import io
import os
import sys
import json
from base64 import b64encode
import xlwings

@extractor.route('/population')
def get_all_assets():
    xlsx_path = resolve("data/Population.xlsx")
    df = pd.read_excel(xlsx_path, sheet_name="population")
    # df['Date Closed'] = df['Date Closed'].dt.strftime('%m-%d-%Y')
    # df['Sale Date'] = df['Sale Date'].dt.strftime('%m-%d-%Y') 
    # df['Sale Date'] = df['Sale Date'].fillna(0) 
    df = df.apply(lambda x: x.fillna(0) if x.dtype.kind in 'biufc' else x.fillna('.'))
    d = df.set_index(['Alias']).to_dict(orient='index')
    j = json.dumps(d)
    #print(j)
    return j