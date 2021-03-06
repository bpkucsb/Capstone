from flask import Flask, render_template, request, redirect
import requests, datetime
import pandas as pd
from bokeh.plotting import output_file, show
from bokeh.resources import CDN
from bokeh.embed import file_html, components
from bokeh.charts import Bar
from bokeh import embed
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///drive_stats'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///drive_app'
db = SQLAlchemy(app)

#class User(db.Model):
#    
#    id = db.Column(db.Integer, primary_key=True)
#    username = db.Column(db.String(80), unique=True)
#    email = db.Column(db.String(120), unique=True)
#
#    def __init__(self, username, email):
#        self.username = username
#        self.email = email
#
#    def __repr(self):
#        return '<User %r>' % self.username

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')

@app.route("/plot")
def plot():

  models = map(str,request.args.getlist('model'))

  total_HD = db.engine.execute("SELECT model, COUNT(serial_number) FROM HDmodel GROUP BY model;")
  failed_HD = db.engine.execute("SELECT model, COUNT(serial_number) FROM HDmodel WHERE sum>0 GROUP BY model;")

  
  total=[]
  for row in total_HD:
     total.append([row[0],float(row[1])])
  total=pd.DataFrame(total,columns=['model','drives'])

  failed=[]
  for row in failed_HD:
     failed.append([row[0],float(row[1])])
  failed=pd.DataFrame(failed,columns=['model','drives'])

  #failure_rate = pd.DataFrame(failed[failed['model'].str.contains('WDC')].drives/(total[total['model'].str.contains('WDC')].drives))
  #model = list(failed[failed['model'].str.contains('WDC')].model)
  
  p = Bar(failed[failed['model'].str.contains('|'.join(models))].drives,cat=list(failed[failed['model'].str.contains('|'.join(models))].model))
  
  script, div = embed.components(p,CDN)

  return render_template("bar.html",script=script,div=div)

if __name__ == '__main__':
  app.debug=True
  app.run(port=33507)
