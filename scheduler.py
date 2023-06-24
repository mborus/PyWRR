import datetime
import time

import database
from recorder import FFMPEGStreamRecording


class SchedulingLoop:
    def __init__(self):
        self._current_treads = []

    def main_loop(self):

        while True:
            f: FFMPEGStreamRecording
            for f in self._current_treads:

                if f.is_ready_to_be_discarded:
                    # todo - thread safe removal from "_current_treads"
                    pass
                else:
                    if f.recording_thread.is_alive():
                        print(f, f.recording_thread.is_alive())
                        print(f._recording_path, f._filesize_approx)

                        if size := f.get_approx_size():
                            database.update_schedule_item_filesize(
                                f.schedule_id, force_filesize=size
                            )
                    else:
                        if f.is_completed and not f.is_ready_to_be_discarded:
                            database.complete_schedule_item(f.schedule_id)
                            database.update_schedule_item_filesize(f.schedule_id)
                            f.is_ready_to_be_discarded = True
                        else:
                            database.abort_schedule_item(f.schedule_id)
                            database.update_schedule_item_filesize(f.schedule_id)
                            f.is_ready_to_be_discarded = True

            time.sleep(5)
            try:
                next_scheduled_item = database.get_next_schedule_item()

                schedule_id = next_scheduled_item["schedule_id"]
                schedule_details = database.get_schedule_item(schedule_id=schedule_id)
                print(schedule_details)

                next_starttime = datetime.datetime.strptime(
                    next_scheduled_item["starttime"][:19], "%Y-%m-%d %H:%M:%S"
                )
                current_time = datetime.datetime.now()
                if next_starttime < current_time:

                    database.activate_schedule_item(schedule_id)

                    f = FFMPEGStreamRecording(
                        schedule_id=schedule_id,
                        duration_min=schedule_details["runtime"],
                        url=schedule_details["station_url"],
                        filepath=schedule_details["filepath"],
                    )
                    f.recording_thread.start()
                    self._current_treads.append(f)

            except database.ScheduledItemNotFound as e:
                print(e)
                pass
            except database.NothingScheduled as e:
                print(e)
                time.sleep(15)


if __name__ == "__main__":
    sl = SchedulingLoop()
    sl.main_loop()
