# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################


#1. / 
#start at the homepage and list all available routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

#2. /api/v1.0/precipitation
# convert query results from precipitation analysis to a dict using date as the key and prcp as the value
# return the JSON representation of the dictionary


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    one_year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)

    data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()

    session.close()

    precip = []
    for date, prcp in data:
        precip_dict = {}
        precip_dict[date] = prcp
        precip.append(precip_dict)
    return jsonify(precip)

#3. /api/v1.0/stations
# return json list of stations from the dataset

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    global station
    sel = [station.id, station.station, station.name, station.latitude, station.longitude, station.elevation]
    query = session.query(*sel).all()

    session.close()

    stations = []
    for id, station, name, latitude, longitude, elevation in query:
        station_dict = {}
        station_dict['id'] = id
        station_dict['station'] = station
        station_dict['name'] = name
        station_dict['latitude'] = latitude
        station_dict['longitude'] = longitude
        station_dict['elevation'] = elevation
        stations.append(station_dict)

    return jsonify(stations)


#4. /api/v1.0/tobs
# query the dates and temp observations of the most active station for the previous year of data
# return JSON list of temp observations for the previous year
@app.route("/api/v1.0/tobs")

def tobs():
    session = Session(engine)

    one_year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
    query = session.query(measurement.date, measurement.tobs).filter(measurement.date >= one_year_ago).\
                    filter(measurement.station == 'USC00519281').all()

    session.close()

    t_obs = []
    for date, tobs in query:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        t_obs.append(tobs_dict)

    return jsonify(t_obs)


#5. /api/v1.0/start and /api/v1.0/start/end
# return a json list of the min, avg and max temp for a specified start or start-end range
#for specified start, calculate TMIN, TAVG, and TMAX for all dates >= to start date
#for specified start and end, caluclate TMIN, TAVG, TMAX for dates from start to end, inclusive

@app.route("/api/v1.0/<start>")
def temps_start(start):
    session = Session(engine)

    sel = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    query = session.query(*sel).filter(measurement.date >= start).all()

    session.close()

    temps = []
    for min, max, avg in query:
        temp_dict = {}
        temp_dict['Min Temperature'] = min
        temp_dict['Max Temperature'] = max
        temp_dict['Avg Temperature'] = avg
        temps.append(temp_dict)

    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def temps_start_end(start, end):
    session = Session(engine)

    sel = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    query = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()

    session.close()

    temps = []
    for min, max, avg in query:
        temp_dict = {}
        temp_dict['Min Temperature'] = min
        temp_dict['Max Temperature'] = max
        temp_dict['Avg Temperature'] = avg
        temps.append(temp_dict)

    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)

