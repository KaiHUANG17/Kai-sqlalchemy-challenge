# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine('sqlite:///Resources/hawaii.sqlite')
# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with = engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    """ List all the available routes """
    return (
        f"Welcome to the Honolulu Climate Analysis App! <br/>"
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start <br/>"
        f"/api/v1.0/start/end"
        
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Route to retrieve precipitation data"""
    
    session = Session(engine)
    
    latest_date = dt.date(2017, 8, 23)
    year_ago_date = latest_date - dt.timedelta(days=365)
    
    precipitation_scores = session.query(Measurement.date, Measurement.prcp)\
                                  .filter(Measurement.date >= year_ago_date)\
                                  .order_by(Measurement.date)\
                                  .all()
    
    session.close()
    precipitation_dict = {date: prcp for date, prcp in precipitation_scores}
    
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Route to retrieve stations"""
    session = Session(engine)
    
    station_list = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    
    session.close()
    
    stations = []
    for station, name, lat, lon, el in station_list:
        station_dict ={
            "station": station,
            "name": name,
            "latitude": lat,
            "longitude": lon,
            "elevation": el
        }
        
        stations.append(station_dict)
        
     
    return jsonify(stations)
    
    
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    tob_query = session.query(Measurement.date, Measurement.tobs)\
                            .filter(Measurement.station == 'USC00519281')\
                            .filter(Measurement.date >= '2016-08-23')\
                            .all() 
    
    session.close()
    
    tobs_list = []
    for date, tobs in tob_query:
        tob_dict = {
            "Date": date,
            "Tobs": tobs
        }
        tobs_list.append(tob_dict)
        
    return jsonify(tobs_list)
    
    
    
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    
    temp_stats = session.query(func.min(Measurement.tobs), 
                               func.avg(Measurement.tobs), 
                               func.max(Measurement.tobs))\
                        .filter(Measurement.date >= start)\
                        .all()
    
    session.close()
    
    temp_stats_list = []
    for Tmin, Tavg, Tmax in temp_stats:
        temp_stats_dict ={
            "TMIN": Tmin,
            "tavg": Tavg,
            "TMAX": Tmax
        }
        temp_stat_list.append(temp_stats_dict)
        
    return jsonify(temp_stats_list)


    
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    start_end = session.query(func.min(Measurment.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
    .filter(Measurement.date >= start)\
    .filter(Measurement.date <= end)\
    .all()
    
    session.close()
    
    temps = []
    for Tmin, Tavg, Tmax in start_end:
        temps_dict = {
            "TMIN": Tmin,
            "TAVG": Tavg,
            "TMAX": Tmax
        }
        temps.append(temps_dict)
        
    return jsonify(temps)


if __name__ == "__main__":
    app.run(debug = True)
