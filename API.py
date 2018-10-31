from flask import Flask
from flask import request, Response
import json
import pandas as pd
from utils.db_tools import DB

path = 'Data/'
handler = DB(path)

app = Flask(__name__)


@app.route('/', methods=['GET'])
def main():
    return 'Deployed'


@app.route('/revenue/', methods=['GET'])
def api_get_revenue():
    revenue = handler.data.groupby(['transaction_date_year']).sum()['sales_amount']
    reply = ('{"revenue" : %s}' % (revenue.to_json()))
    return Response(reply, status=200, mimetype='application/json')


@app.route('/activeusers/', methods=['GET'])
def api_get_activeusers():
    df = handler.data.drop_duplicates(subset=['user', 'transaction_date_year'], keep='first')
    activeusers = df.groupby(['transaction_date_year']).count()['user']
    reply = ('{"activeusers" : %s}' % (activeusers.to_json()))
    return Response(reply, status=200, mimetype='application/json')


@app.route('/newusercount/', methods=['GET'])
def api_get_newusercount():
    df = handler.data.drop_duplicates(subset=['user', 'join_date_year'], keep='first')
    newusercount = df.groupby(['join_date_year']).count()['user']
    reply = ('{"newusercount" : %s}' % (newusercount.to_json()))
    return Response(reply, status=200, mimetype='application/json')


@app.route('/arpau/', methods=['GET'])
def api_get_arpau():
    revenue = handler.data.groupby(['transaction_date_year']).sum()['sales_amount']
    df = handler.data.drop_duplicates(subset=['user', 'transaction_date_year'], keep='first')
    activeusers = df.groupby(['transaction_date_year']).count()['user']
    arpau = revenue / activeusers
    reply = ('{"arpau" : %s}' % (arpau.to_json()))
    return Response(reply, status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
