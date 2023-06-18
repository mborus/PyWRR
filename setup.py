import datetime
import database

# database.DATABASE_NAME = f'main {datetime.datetime.now():%Y-%m-%d_%H-%M-%S}'

database.setup_database_tables()

database.add_station(station_id="LOS40",
                     station_name="LOS 40",
                     station_url="https://playerservices.streamtheworld.com/api/livestream-redirect/LOS40.mp3")

database.add_station(station_id="RSH",
                     station_name="Radio Schleswig Holstein",
                     station_url="https://streams.rsh.de/rsh-live/aac-64")

database.add_station(station_id="AUTO-SYLT",
                     station_name="Autozugradio Sylt",
                     station_url="https://autozugradio-stream31.radiohost.de/autozugradio-blau_aac-48?ref=sylt")

database.add_station(station_id="DMY",
                     station_name="DUMMY",
                     station_url="https://dummy")


database.delete_station(station_id="DMY")


database.add_schedule_item(station_id='RSH', starttime=datetime.datetime.now(), runtime=2, filepath=None)
database.add_schedule_item(station_id='LOS40', starttime=datetime.datetime.now() + datetime.timedelta(seconds=3600),
                           runtime=5, filepath=None)

print(database.get_next_schedule_item())
try:
    database.activate_schedule_item(1)
except database.DatabaseException:
    pass

print(database.get_next_schedule_item())

print(database.get_all_stations())
print(database.get_scheduled_events(future_events=True, completed_events=False, active_events=False))
