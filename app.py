#Import Flask and Dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

# 1. Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

# 2. Flask Setup- Create an app, being sure to pass __name__
app = Flask(__name__)

# 3. Flask Routes- Define what to do when a user hits the index route
#Home Page & List all routes that are available.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

#Convert the query results to a dictionary using date as the key and prcp as the value & 
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    max_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

    # Get the first element of the tuple
    max_date = max_date[0]

    # Calculate the date 1 year ago from today
    # The days are equal 366 so that the first day of the year is included
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
    
    # Perform a query to retrieve the data and precipitation scores
    results_precipitation = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago).all()
    session.close()
    
    # Convert list of tuples into normal list
    precipitation_dict = dict(results_precipitation)

    return jsonify(precipitation_dict)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations(): 

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query stations
    results_stations = session.query(measurement.station).group_by(measurement.station).all()
    session.close()
    
    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results_stations))

    return jsonify(stations_list)

# Query info on most active station for the last year & Return a JSON list of temp (TOBS).
@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query tobs
    tobs = session.query(measurement.tobs).filter(measurement.station == 'USC00519281' ).\
            filter(measurement.date >= '2017,8,23').all()
    
    session.close()
    
    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(tobs))
    
    return jsonify (tobs_list)

# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
app.route("/api/v1.0/<start>")
def start(start=None):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query TMIN, TAVG, and TMAX for start
    from_start = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), 
                               func.max(measurement.tobs)).filter(measurement.date >= start).group_by(measurement.date).all()
    session.close()
    
    # Convert list of tuples into normal list
    from_start_list=list(from_start)
    
    return jsonify(from_start_list)

# When given the start AND end date, calculate the TMIN, TAVG, and TMAX.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query TMIN, TAVG, and TMAX for start & end
    between_dates = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs),
                    func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).group_by(measurement.date).all()
    session.close()
    
    # Convert list of tuples into normal list   
    between_dates_list=list(between_dates)
    
    return jsonify(between_dates_list)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)