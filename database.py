import datetime
import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path

# Global variable for the database name
DATABASE_NAME = "main.db"

class DatabaseException(Exception):
    pass


class NothingScheduled(Exception):
    pass


class ScheduledItemNotFound(Exception):
    pass


# Reusable cursor function
@contextmanager
def get_cursor(commit=True):
    # Connect to the database (create if it doesn't exist)
    conn = sqlite3.connect(DATABASE_NAME)
    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    yield cursor
    if commit:
        conn.commit()
    conn.close()


def setup_database_tables():
    with get_cursor() as cursor:
        # Create the "stations" table
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS stations (
                            station_id TEXT(10) PRIMARY KEY,
                            station_name TEXT,
                            station_url TEXT,
                            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
        )

        # Create the "schedule" table
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS schedule (
                            schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            station_id TEXT(10),
                            starttime DATETIME,
                            runtime INTEGER,
                            repeat_rule TEXT,
                            active INTEGER DEFAULT 0,
                            completed INTEGER DEFAULT 0,
                            aborted INTEGER DEFAULT 0,
                            filepath TEXT,
                            filesize INTEGER DEFAULT 0,
                            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (station_id) REFERENCES stations(station_id))"""
        )


def add_station(station_id, station_name, station_url):
    with get_cursor(commit=True) as cursor:
        # Check if the station already exists
        cursor.execute(
            "SELECT COUNT(*) FROM stations WHERE station_id = ?", (station_id,)
        )
        count = cursor.fetchone()[0]

        if count == 0:
            # Station doesn't exist, insert a new record
            cursor.execute(
                "INSERT INTO stations (station_id, station_name, station_url) VALUES (?, ?, ?)",
                (station_id, station_name, station_url),
            )
        else:
            # Station exists, update the record
            cursor.execute(
                "UPDATE stations SET station_name = ?, station_url = ? WHERE station_id = ?",
                (station_name, station_url, station_id),
            )


def delete_station(station_id):
    with get_cursor(commit=True) as cursor:
        # Check if there are any future scheduled recordings for the station
        current_datetime = datetime.datetime.utcnow()
        cursor.execute(
            "SELECT COUNT(*) FROM schedule WHERE station_id = ? AND starttime > ?",
            (station_id, current_datetime),
        )
        count = cursor.fetchone()[0]

        if count > 0:
            raise ValueError(
                "Cannot delete the station. There are still future scheduled recordings."
            )

        # Delete the station from the "stations" table
        cursor.execute("DELETE FROM stations WHERE station_id = ?", (station_id,))


def get_all_stations():
    with get_cursor() as cursor:
        # Retrieve all stations from the table
        cursor.execute("SELECT * FROM stations")
        stations = cursor.fetchall()

        if not stations:
            return []

        # Get the column names from the cursor description
        column_names = [column[0] for column in cursor.description]

        # Create a list of dictionaries, where each dictionary represents a station
        station_list = []
        for station in stations:
            station_dict = {column_names[i]: value for i, value in enumerate(station)}
            station_list.append(station_dict)

        return station_list


def add_schedule_item(station_id, starttime, runtime, filepath=None, repeat_rule=None):
    if filepath is None:
        if isinstance(starttime, datetime.datetime):
            filepath = f"{station_id} {starttime:%Y-%m-%d %H-%M-%S}.ts"
        else:
            filepath = f"{station_id} {starttime}.ts"

    # filter forbidden chars from filepath
    def filter_filename(filename):
        forbidden_chars = r'[<>:"/\\|?*]'
        return re.sub(forbidden_chars, '_', filename)

    filepath = filter_filename(filepath)

    with get_cursor() as cursor:
        # Check if an entry already exists for the station and starttime
        cursor.execute(
            "SELECT COUNT(*) FROM schedule WHERE station_id = ? AND starttime = ?",
            (station_id, starttime),
        )
        count = cursor.fetchone()[0]

        if count == 0:
            # Entry doesn't exist, insert a new record
            cursor.execute(
                "INSERT INTO schedule (station_id, starttime, runtime, repeat_rule, filepath) VALUES (?, ?, ?, ?, ?)",
                (station_id, starttime, runtime, repeat_rule, filepath),
            )
        else:
            # Entry exists, update the record
            cursor.execute(
                "UPDATE schedule SET runtime = ?, repeat_rule = ?, filepath = ? WHERE station_id = ? AND starttime = ?",
                (runtime, repeat_rule, filepath, station_id, starttime),
            )


def delete_scheduled_event(schedule_id):
    with get_cursor() as cursor:
        # Check if the schedule item exists
        cursor.execute(
            "SELECT COUNT(*) FROM schedule WHERE schedule_id = ?", (schedule_id,)
        )
        count = cursor.fetchone()[0]

        if count == 0:
            raise DatabaseException("Schedule item does not exist.")

        # Check if the schedule item is active
        cursor.execute(
            "SELECT active FROM schedule WHERE schedule_id = ?", (schedule_id,)
        )
        active = cursor.fetchone()[0]

        if active == 1:
            raise DatabaseException("Cannot delete active schedule item.")

        # Check if the schedule item is completed
        cursor.execute(
            "SELECT completed FROM schedule WHERE schedule_id = ?", (schedule_id,)
        )
        completed = cursor.fetchone()[0]

        if completed == 1:
            raise DatabaseException(
                "Cannot delete schedule item. It is already completed."
            )

        # Delete the specified schedule item from the table
        cursor.execute("DELETE FROM schedule WHERE schedule_id = ?", (schedule_id,))


def get_next_schedule_item():
    with get_cursor() as cursor:
        # Retrieve the next schedule item that is not active, not completed, and not aborted
        cursor.execute(
            "SELECT * FROM schedule WHERE active = 0 AND completed = 0 AND aborted = 0 ORDER BY starttime ASC LIMIT 1"
        )
        schedule_item = cursor.fetchone()

        if schedule_item is None:
            raise NothingScheduled("No schedule item found.")

        # Get the column names from the cursor description
        column_names = [column[0] for column in cursor.description]

        # Create a dictionary using column names as keys and schedule item values as values
        schedule_dict = {
            column_names[i]: value for i, value in enumerate(schedule_item)
        }
        return schedule_dict


def get_schedule_item(schedule_id):
    with get_cursor() as cursor:
        # Retrieve the schedule item with its station information
        cursor.execute(
            """SELECT schedule.*, stations.station_name, stations.station_url
                          FROM schedule
                          INNER JOIN stations ON schedule.station_id = stations.station_id
                          WHERE schedule.schedule_id = ?""",
            (schedule_id,),
        )
        schedule_item = cursor.fetchone()

        if schedule_item is None:
            raise ScheduledItemNotFound(f"Schedule_id {schedule_id} not in database.")

        # Get the column names from the cursor description
        column_names = [column[0] for column in cursor.description]

        # Create a dictionary using column names as keys and schedule item values as values
        schedule_dict = {
            column_names[i]: value for i, value in enumerate(schedule_item)
        }

        return schedule_dict


def activate_schedule_item(schedule_id):
    with get_cursor() as cursor:
        # Check if the schedule item exists
        cursor.execute(
            "SELECT COUNT(*) FROM schedule WHERE schedule_id = ?", (schedule_id,)
        )
        count = cursor.fetchone()[0]

        if count == 0:
            raise DatabaseException("Schedule item does not exist.")

        # Check if the schedule item is already active, completed, or aborted
        cursor.execute(
            "SELECT active, completed, aborted FROM schedule WHERE schedule_id = ?",
            (schedule_id,),
        )
        result = cursor.fetchone()
        active, completed, aborted = result

        if active == 1 or completed == 1 or aborted == 1:
            raise DatabaseException(
                "Cannot activate schedule item. It is already active, completed, or aborted."
            )

        # Update the active field of the specified schedule item
        cursor.execute(
            "UPDATE schedule SET active = 1 WHERE schedule_id = ?", (schedule_id,)
        )


def complete_schedule_item(schedule_id):
    with get_cursor() as cursor:
        # Check if the schedule item exists
        cursor.execute(
            "SELECT COUNT(*) FROM schedule WHERE schedule_id = ?", (schedule_id,)
        )
        count = cursor.fetchone()[0]

        if count == 0:
            raise DatabaseException("Schedule item does not exist.")

        # Check if the schedule item is active
        cursor.execute(
            "SELECT active FROM schedule WHERE schedule_id = ?", (schedule_id,)
        )
        active = cursor.fetchone()[0]

        if active != 1:
            raise DatabaseException("Cannot complete schedule item. It is not active.")

        # Update the completed and active fields of the specified schedule item
        cursor.execute(
            "UPDATE schedule SET completed = 1, active = 0 WHERE schedule_id = ?",
            (schedule_id,),
        )


def abort_schedule_item(schedule_id):
    with get_cursor() as cursor:
        # Check if the schedule item exists
        cursor.execute(
            "SELECT COUNT(*) FROM schedule WHERE schedule_id = ?", (schedule_id,)
        )
        count = cursor.fetchone()[0]

        if count == 0:
            raise DatabaseException("Schedule item does not exist.")

        # Check if the schedule item is completed
        cursor.execute(
            "SELECT completed FROM schedule WHERE schedule_id = ?", (schedule_id,)
        )
        completed = cursor.fetchone()[0]

        if completed == 1:
            raise DatabaseException(
                "Cannot abort schedule item. It is already completed."
            )

        # Update the aborted field of the specified schedule item
        cursor.execute(
            "UPDATE schedule SET aborted = 1 WHERE schedule_id = ?", (schedule_id,)
        )


def update_schedule_filepath(schedule_id, filepath):
    with get_cursor() as cursor:
        # Check if the schedule item exists
        cursor.execute(
            "SELECT COUNT(*) FROM schedule WHERE schedule_id = ?", (schedule_id,)
        )
        count = cursor.fetchone()[0]

        if count == 0:
            raise DatabaseException("Schedule item does not exist.")

        # Check if the schedule item is active, completed, or aborted
        cursor.execute(
            "SELECT active, completed, aborted FROM schedule WHERE schedule_id = ?",
            (schedule_id,),
        )
        result = cursor.fetchone()
        active, completed, aborted = result

        if active == 1 or completed == 1 or aborted == 1:
            raise DatabaseException(
                "Cannot update filepath. Schedule item is active, completed, or aborted."
            )

        # Update the filepath field of the specified schedule item
        cursor.execute(
            "UPDATE schedule SET filepath = ? WHERE schedule_id = ?",
            (filepath, schedule_id),
        )


def update_schedule_item_filesize(schedule_id):
    with get_cursor() as cursor:
        # Check if the schedule item exists
        cursor.execute(
            "SELECT COUNT(*) FROM schedule WHERE schedule_id = ?", (schedule_id,)
        )
        count = cursor.fetchone()[0]

        if count == 0:
            raise DatabaseException("Schedule item does not exist.")

        # Retrieve the filepath for the schedule item
        cursor.execute(
            "SELECT filepath FROM schedule WHERE schedule_id = ?", (schedule_id,)
        )
        filepath = cursor.fetchone()[0]

        # Retrieve the file size
        # Check if the file exists
        if os.path.exists(filepath):
            filesize = os.path.getsize(filepath)
        else:
            filesize = 0

        # Update the filesize field of the specified schedule item
        cursor.execute(
            "UPDATE schedule SET filesize = ? WHERE schedule_id = ?",
            (filesize, schedule_id),
        )

        return filesize


def get_scheduled_events(future_events=True, active_events=True, completed_events=True):
    with get_cursor() as cursor:
        # Build the SQL query based on the provided filters
        filters = []
        if future_events:
            filters.append("(completed = 0 AND active = 0 AND aborted = 0)")
        if completed_events:
            filters.append("completed = 1")
        if active_events:
            filters.append("active = 1")

        # Join the filters with "OR" conditions
        filters_query = " OR ".join(filters)

        # Retrieve the scheduled events based on the filters
        query = f"SELECT * FROM schedule WHERE {filters_query}"
        cursor.execute(query)
        events = cursor.fetchall()

        if not events:
            return []

        # Get the column names from the cursor description
        column_names = [column[0] for column in cursor.description]

        # Create a list of dictionaries, where each dictionary represents an event
        event_list = []
        for event in events:
            event_dict = {column_names[i]: value for i, value in enumerate(event)}
            event_list.append(event_dict)

        return event_list


if not Path(DATABASE_NAME).exists():
    setup_database_tables()

