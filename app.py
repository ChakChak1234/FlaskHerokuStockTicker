import requests
import pandas
import bokeh
from bokeh.plotting import figure
from bokeh.embed import components
import bokeh.sampledata
from flask import Flask, render_template, request, redirect, session
import datetime

app = Flask(__name__)

app.vars = {}

@app.route('/')
def main():
    return redirect('/index')


@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/graph', methods=['POST'])
def graph():
    #    if request.method == 'POST':
    app.vars['ticker'] = request.form['ticker']
    app.vars['start_date'] = request.form['start_date']
    app.vars['end_date'] = request.form['end_date']

    api_url = 'https://www.quandl.com/api/v3/datasets/WIKI/%s/data.json?api_key=n36teYQNRWq1xmudWvm3' % app.vars['ticker']
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    raw_data = session.get(api_url)

    a = raw_data.json()
    df = pandas.DataFrame(a['dataset_data']['data'], columns=a['dataset_data']['column_names'])

    df['Date'] = pandas.to_datetime(df['Date']).dt.date

    df = df[['Date', 'Open', 'Adj. Open', 'Close', 'Adj. Close']]

    start_date = datetime.datetime.strptime(app.vars['start_date'], "%m/%d/%Y").date()
    end_date = datetime.datetime.strptime(app.vars['end_date'], "%m/%d/%Y").date()
    df = df.loc[(df['Date'] > start_date) & (df['Date'] < end_date)]

    p = figure(title='Stock prices for %s' % app.vars['ticker'],
               x_axis_label='date',
               x_axis_type='datetime')

    if request.form.get('open'):
        p.line(x=df['Date'].values, y=df['Open'].values, line_width=2, line_color="red", legend_label='Open')
    if request.form.get('adj_open'):
        p.line(x=df['Date'].values, y=df['Adj. Open'].values, line_width=2, line_color="purple", legend_label='Adj. Open')
    if request.form.get('close'):
        p.line(x=df['Date'].values, y=df['Close'].values, line_width=2, line_color="blue", legend_label='Close')
    if request.form.get('adj_close'):
        p.line(x=df['Date'].values, y=df['Adj. Close'].values, line_width=2, line_color="green", legend_label='Adj. Close')
    script, div = components(p)
    return render_template('graph.html', script=script, div=div)

if __name__ == '__main__':
    app.run(port=33507)