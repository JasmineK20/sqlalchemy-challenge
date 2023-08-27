# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Convert the query results from your precipitation analysis to a dictionary using date as the key and prcp as the value

@app.route("/api/v1.0/precipitation")
def precipitation():
   
    year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)
    print(year_ago)

    prcp_scores = session.query(Measurement.date, func.avg(Measurement.prcp)).\
                    filter(Measurement.date >= year_ago).\
                    group_by(Measurement.date).all()

    precipitaton_query_values = []
    for prcp, date in prcp_scores:
        precipitation_dict = {}
        precipitation_dict["precipitation"] = prcp
        precipitation_dict["date"] = date
        precipitaton_query_values.append(precipitation_dict)
    return jsonify(precipitaton_query_values) 

# Return a JSON list of stations from the dataset

@app.route("/api/v1.0/stations")
def station(): 

    station_query = session.query(Station.station,Station.id).all()

    stations_values = []
    for station, id in station_query:
        stations_values_dict = {}
        stations_values_dict['station'] = station
        stations_values_dict['id'] = id
        stations_values.append(stations_values_dict)
    return jsonify (stations_values) 

#Query the dates and temperature observations of the most-active station for the previous year of data, return a JSON list

@app.route("/api/v1.0/tobs") 
def tobs():
     
    last_year_query = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first() 

    last_year_query = []
    for date in last_year_query:
        last_year_dict = {}
        last_year_dict["date"] = date
        last_year_query.append(last_year_dict) 
    print(last_year_query)

    query_startdate = dt.date(2017, 8, 23)-dt.timedelta(days =365) 
    print(query_startdate) 

    active_station= session.query(Measurement.station, func.count(Measurement.station)).\
        order_by(func.count(Measurement.station).desc()).\
        group_by(Measurement.station).first()
    most_active = active_station[0] 

    session.close() 

    print(most_active)

    dates_tobs_last_year_query = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
        filter(Measurement.date > query_startdate).\
        filter(Measurement.station == most_active) 

    dates_tobs_last_year_values = []
    for date, tobs, station in dates_tobs_last_year_query:
        dates_tobs_dict = {}
        dates_tobs_dict["date"] = date
        dates_tobs_dict["tobs"] = tobs
        dates_tobs_dict["station"] = station
        dates_tobs_last_year_values.append(dates_tobs_dict)
        
    return jsonify(dates_tobs_last_year_values) 

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for start date

@app.route("/api/v1.0/<date>")
def startDateOnly(date):
    date = dt.datetime.strptime(date,"%m-%d-%Y")
    start_temp_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= date).all()
    results = list(np.ravel(start_temp_results))
    return jsonify(results)


#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for start to end 

@app.route("/api/v1.0/<start>/<end>")
def startDateEndDate(start,end):
    start = dt.datetime.strptime(start,"%m-%d-%Y")
    end = dt.datetime.strptime(end,"%m-%d-%Y")
    start_end_temp_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    results_startend = list(np.ravel(start_end_temp_results))
    return jsonify(results_startend)

if __name__ == "__main__":
    app.run(debug=True)







   







