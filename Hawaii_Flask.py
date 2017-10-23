from flask import Flask, jsonify
import json
import sqlalchemy
import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func, desc, extract
from dateutil.relativedelta import relativedelta

engine = create_engine("sqlite:///hawaii.db", echo=False)
Base = automap_base()
Base.prepare(engine, reflect=True)

m = Base.classes.Measurements
s = Base.classes.Stations

session = Session(bind=engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    perp = "<p>Please Click <a href='/api/v1.0/precipitation'>Here</a> for the Precipitation API</p>"
    station = "<p>Please Click <a href='/api/v1.0/stations'>Here</a> for the Stations API</p>"
    tobs = "<p>Please Click <a href='/api/v1.0/tobs'>Here</a> for the Temperature Observations API</p>"
    Enter_date = "<p>Please Click <a href='/api/v1.0/<start_date>'>Here</a> and replace date in YYYY-MM-DD between 2010-01-01 and 2017-08-23 for the Daily Measure API on that Date</p>"
    Between_dates = "<p>Please Click <a href='/api/v1.0/<date1>/<date2>'>Here</a> and Replace date1 with Start Date and date2 with End Date by having a '-'to get the Daily Measure those two dates</p>"
    return perp + station + tobs + Enter_date + Between_dates


@app.route("/api/v1.0/date")
def dailyDetails():
    return "<p>Replace date in YYYY-MM-DD between 2017-07-01 and 2017-08-23 for the Daily Measure API on that Date</p>"

@app.route("/api/v1.0/date1-date2")
def BetweenDetails():
    return "<p>Replace date1 with Start Date and date2 with End Date by having a '-'to get the Daily Measure those two dates</p>"

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query for the dates and temperature observations from the last year.
        Convert the query results to a Dictionary using date as the key and tobs as the value.
        Return the json representation of your dictionary"""
    precipList = []
    prec_qry = session.query(s.name, m.date, m.prcp).filter(
        m.date >= '2017-07-01').order_by(m.date)
    for p in prec_qry:

        precipList.append({"station": p[0], "date": p[1], "prcp": p[2]})

    return jsonify(precipList)


@app.route("/api/v1.0/stations")
def stations():
    # Return a json list of stations from the dataset.
    stations = session.query(
        s.station, s.name).distinct().order_by(s.station).all()
    stationList = []
    for station in stations:
        stationList.append({"station": station[0], "name": station[1]})

    return jsonify(stationList)


@app.route("/api/v1.0/tobs")
def tobs():
    # Return a json list of Temperature Observations (tobs) for the previous year
    max_observation = session.query(m.date).order_by(m.date.desc()).first()
    last_year = max_observation[0] - relativedelta(years=1)
    tobs = session.query(s.name, m.date, m.tobs).filter(
        m.date >= last_year).filter(m.station == s.station).order_by(m.date).all()
    tobsList = []
    for t in tobs:
        tobsList.append(
            {"station": t[0], "date": t[1], "temperature observation": t[2]})

    return jsonify(tobsList)


@app.route("/api/v1.0/<start_date>")
def get_date(start_date):
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    # Return a json list of th  e minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    print('Inside Date')
    print(start_date)
    query = session.query(func.min(m.tobs)).filter(m.date > datetime.datetime.today()- relativedelta(years=1) ).scalar()
    print(query)
    minimum = session.query(func.min(m.tobs)).filter(m.date >= start_date).scalar()

    average = session.query(func.round(func.avg(m.tobs))
                            ).filter(m.date >= start_date).scalar()

    maximum = session.query(func.max(m.tobs)).filter(m.date >= start_date).scalar()

    result = [{"Minimum": minimum}, {"Average": average}, {"Maximum": maximum}]
    print(result)
    return jsonify(result)


@app.route("/api/v1.0/<start_date>/<end_date>")
def startEnd(start_date, end_date):
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    # Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    print('inside in multiple')
    minimum = session.query(func.min(m.tobs)).filter(
        m.date.between(start_date, end_date)).scalar()
    average = session.query(func.round(func.avg(m.tobs))).filter(
        m.date.between(start_date, end_date)).scalar()
    maximum = session.query(func.max(m.tobs)).filter(
        m.date.between(start_date, end_date)).scalar()

    result = [{"Minimum": minimum}, {"Average": average}, {"Maximum": maximum}]
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
