from pathlib import Path

import markdown
from database import (
    DatabaseException,
    add_schedule_item,
    add_station,
    delete_scheduled_event,
    delete_station,
    get_all_stations,
    get_scheduled_events,
)
from flask import Flask, flash, redirect, render_template, request, send_file
from settings import RECORDING_PATH

app = Flask(__name__)

# turn off caching while prototyping
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

app.secret_key = "your_secret_key"  # Set your secret key here


@app.route("/")
def hello_world():  # put application's code here
    return render_template("index.html", title="Home")


@app.route("/settings")
def hello_world1():  # put application's code here
    flash("Deleted Contact!")
    return render_template("settings.html")


@app.route("/stations")
def display_stations():
    # Retrieve all stations
    all_stations = get_all_stations()

    # Render the stations in an HTML table
    return render_template("stations.html", stations=all_stations)


@app.route("/add-station", methods=["POST"])
def add_station_endpoint():
    station_id = request.form.get("station_id")
    station_name = request.form.get("station_name")
    station_url = request.form.get("station_url")

    try:
        add_station(station_id, station_name, station_url)
        return redirect(
            "/stations", code=303
        )  # Redirect to the desired page after successful addition
    except DatabaseException as e:
        return render_template("error.html", error=str(e))


@app.route("/delete-station/<station_id>", methods=["POST"])
def delete_station_endpoint(station_id):
    try:
        delete_station(station_id)  # Implement your delete_station function
        return redirect(
            "/stations", code=303
        )  # Redirect to the desired page after successful deletion
    except DatabaseException as e:
        return render_template("error.html", error=str(e))


@app.route("/future-events")
def future_events():
    # Retrieve future events using the get_scheduled_events function with appropriate filters
    future_events = get_scheduled_events(
        future_events=True, active_events=False, completed_events=False
    )

    # Render the future events in an HTML template
    return render_template("future_events.html", events=future_events)


@app.route("/running-events")
def running_events():
    # Retrieve future events using the get_scheduled_events function with appropriate filters
    running_events = get_scheduled_events(
        future_events=False, active_events=True, completed_events=False
    )

    # Render the future events in an HTML template
    return render_template("running_events.html", events=running_events)


@app.route("/completed-events")
def completed_events():
    # Retrieve completed events using the get_scheduled_events function with appropriate filters
    completed_events = get_scheduled_events(
        future_events=False, active_events=False, completed_events=True
    )

    # Render the completed events in an HTML template
    return render_template("completed_events.html", events=completed_events)


@app.route("/add-schedule", methods=["POST"])
def add_schedule_endpoint():
    station_id = request.form.get("station_id")
    starttime = request.form.get("starttime")
    runtime = request.form.get("runtime")
    repeat_rule = request.form.get("repeat_rule")

    try:
        add_schedule_item(
            station_id=station_id,
            starttime=starttime,
            runtime=runtime,
            repeat_rule=repeat_rule,
        )
        return redirect(
            "/future-events", code=303
        )  # Redirect to the desired page after successful event addition
    except DatabaseException as e:
        return render_template("error.html", error=str(e))


@app.route("/delete-schedule/<int:schedule_id>", methods=["POST"])
def delete_schedule(schedule_id):
    try:
        delete_scheduled_event(schedule_id)
        return redirect("/future-events", code=303)
    except DatabaseException as e:
        return render_template("error.html", error=str(e))


@app.route("/archive/<path:filepath>")
def download_file(filepath):
    # Get the absolute path to the file

    abs_filepath = Path(RECORDING_PATH, filepath)

    # Serve the file for download
    return send_file(
        abs_filepath, as_attachment=False, mimetype="audio/mp2t"
    )  # true für download


@app.route("/about")
def about_page():
    with open("readme.md", "rb") as file:
        markdown_content = file.read().decode("utf-8")
    html_content = markdown.markdown(markdown_content)
    return render_template("about.html", content=html_content)


# if __name__ == '__main__':
#    app.run(host="0.0.0.0", port=9000)
