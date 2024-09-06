# Import the necessary libraries
import numpy as np
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

# Set up the database engine for SQLite
engine = create_engine(r"sqlite:///C:\Users\zarap\OneDrive\UofT BootCamp\Class Project\sqlalchemy-challenge\SurfsUp\Resources\hawaii.sqlite")

# Reflect the existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create an app, pass __name__
app = Flask(__name__)

# Define the homepage route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return precipitation data for the last year as json."""
    # Create a session link from Python to the DB
    session = Session(engine)
    
    # Calculate the date 1 year ago from the last data point in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)

# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations as json."""
    # Create a session link from Python to the DB
    session = Session(engine)
    
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert the list of tuples into a normal list
    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

# Define the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the most active station for the last year as json."""
    # Create a session link from Python to the DB
    session = Session(engine)
    
    # Calculate the date 1 year ago from the last data point in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Find the most active station
    active_station = session.query(Measurement.station, func.count(Measurement.id)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).first()[0]

    # Query the last 12 months of temperature observations for the most active station
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == active_station).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Convert the list of tuples into a normal list
    tobs_list = list(np.ravel(results))
    return jsonify(tobs_list)

# Define the dynamic route for start date
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    """Return minimum, average, and maximum temperatures from the start date or between the start and end date as json."""
    # Create a session link from Python to the DB
    session = Session(engine)
    
    # Select statement for the minimum, average, and maximum temperature
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # If no end date is provided, query for all dates greater than or equal to the start date
    if not end:
        results = session.query(*sel).filter(Measurement.date >= start).all()
    else:
        # If end date is provided, query for all dates between the start and end date
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Convert the list of tuples into a normal list
    temps = list(np.ravel(results))
    return jsonify(temps)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
