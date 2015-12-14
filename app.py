from flask import Flask, render_template, request, redirect
import pandas
import Quandl
import time
import datetime
from bokeh.plotting import figure
from bokeh.embed import components

app_lulu = Flask(__name__)

app_lulu.colors = {
    'Black': '#000000',
    'Red':   '#FF0000',
    'Green': '#00FF00',
    'Blue':  '#0000FF',
}
app_lulu.colorlist = ['Black','Red','Green','Blue']

app_lulu.vars={}
app_lulu.stock_data=[]
app_lulu.err_msg=''
app_lulu.script=''
app_lulu.div=''
app_lulu.price_cnt=0

@app_lulu.route('/')
def main_entry():
    return redirect('/main_input')

@app_lulu.route('/main_input',methods=['GET','POST'])
def main_input():
    if request.method == 'GET':
    	return render_template('user_input_page.html')
    else:
        #request was a POST
        app_lulu.vars['stock'] = request.form.get('stock_symbol',None)
        app_lulu.vars['price'] = request.form.getlist('prices',None)
        app_lulu.price_cnt = len(app_lulu.vars['price'])        

        #if app_lulu.vars['stock'] != None and app_lulu.price_cnt > 0:
        #    f = open('%s.txt'%(app_lulu.vars['stock']),'w')
	#    for i in range(app_lulu.price_cnt):
	#	f.write('%s\n'%(app_lulu.vars['price'][i]))
        #    f.close() 
        
        return redirect('/graph_decision') 

@app_lulu.route('/graph_decision')
def decision():
    if app_lulu.vars['stock'] != None and app_lulu.price_cnt > 0:

	time_now = datetime.date.fromtimestamp(time.time())
        time_delta = datetime.timedelta(days=-31)
        time_start = time_now + time_delta 
        start_date = time_start.strftime('%Y-%m-%d')
        end_date = time_now.strftime('%Y-%m-%d')

        search_symbol = 'wiki/'+str(app_lulu.vars['stock'])
        try:
            app_lulu.stock_data = Quandl.get(search_symbol, authtoken="YMWY8Fe5ywYG3uWQ85m7",\
                                             trim_start=start_date,trim_end=end_date,\
                                             collapse="daily")
            r = figure(x_axis_type = "datetime")
            for i in range(app_lulu.price_cnt): 
            	r.line(app_lulu.stock_data.index.values, \
                       app_lulu.stock_data[app_lulu.vars['price'][i]].values,\
                       color=app_lulu.colors[app_lulu.colorlist[i]],\
                       legend=app_lulu.vars['price'][i])
            r.title = "Stock Prices-"+str(app_lulu.vars['stock'])
            r.grid.grid_line_alpha=0.3
            app_lulu.script, app_lulu.div = components(r)             
  
            return redirect('/graph_lulu')
        except Quandl.Quandl.DatasetNotFound:
            app_lulu.err_msg = 'Stock symbol not found in the Quandl Wiki data set!'
            return redirect('/error_lulu') 
    else:
        app_lulu.err_msg = 'No stock symbol and/or prices selected!'
        return redirect('/error_lulu')
  
@app_lulu.route('/graph_lulu',methods=['GET','POST'])
def graph():
    if request.method == 'GET':
        return render_template('graph_page.html',script=app_lulu.script,div=app_lulu.div)
    else:
        return redirect('/main_input')

@app_lulu.route('/error_lulu',methods=['GET','POST'])
def error_stuff():
    if request.method == 'GET':
        return render_template('error_page.html',err=app_lulu.err_msg)
    else:
        return redirect('/main_input')


if __name__ == '__main__':
    app_lulu.run(port=33507)

