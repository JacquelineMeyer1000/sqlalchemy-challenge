#Import Flask and Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

import datetime as dt

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
def home():
    session = Session(engine)
    print("Server received request for 'Home' page...")
    return "Available Routes: /api/v1.0/precipitation, /api/v1.0/stations, /api/v1.0/tobs, /api/v1.0/start, /api/v1.0/start/end" 
    session.close()
    

#Return a JSON list of precipitation from the dataset.
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
def start(start):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query TMIN, TAVG, and TMAX for start
    start_min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).all()
    start_max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    start_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()) 
    session.close()

    return f'The minimum temperature from {start} to present was {start_min[0][0]}. The maximum temperature was {start_max[0][0]}. The average temperature was {start_avg[0][0]}'


# When given the start AND end date, calculate the TMIN, TAVG, and TMAX.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query TMIN, TAVG, and TMAX for start & end
    start_end_min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date < end).all()
    start_end_max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date < end).all()
    start_end_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date < end).all()
    session.close()
    
    return f'The minimum temperature from {start} to {end} was {start_end_min[0][0]}. The maximum temperature was {start_end_max[0][0]}. The average temperature was {start_end_avg[0][0]}'

if __name__ == "__main__":
    app.run(debug=True)