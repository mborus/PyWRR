import time
import datetime
import shlex
from threading import Thread
import subprocess
from pathlib import Path


class ScheduledRecordingException(Exception):
    pass


class FFMPEGStreamRecording:
    def __init__(self, schedule_id, url, duration_min=60, filepath=None):
        self.schedule_id = schedule_id
        self.url = url
        self.duration_min = duration_min
        self.starttime = None
        self.runtime_sec = None
        self.active = False
        self.filename = filepath
        self.process = None
        self.recording_thread = Thread(target=self.do_recording)
        self.recording_thread.daemon = True
        self.stderr_thread = None
        self.is_aborted = False
        self.is_completed = False
        self.is_ready_to_be_discarded = False  # when finalized in the database
        self.log = []

        if not self.url.startswith('http'):
            raise ScheduledRecordingException(f'Url {self.url} not correct')
        if self.duration_min < 0 or self.duration_min >= 24 * 60:
            raise ScheduledRecordingException(f'Recording duration {self.duration_min} out of limits.')

        # TODO - validate filename doesn't exist!

    def __repr__(self):
        return f"FFMPEG Recording #{self.schedule_id} - {self.starttime} - {self.url}"

    @property
    def get_ffmpeg_call(self):
        command = ['ffmpeg',
                   # overwrite existing file
                   '-y',
                   # input url
                   '-i', self.url,
                   # do not reencode
                   '-codec', 'copy',
                   # duration: set to a day and manually abbort
                   '-t',
                   # f"{datetime.datetime(1980, 1, 1) + datetime.timedelta(seconds=60 * self.duration_min):%H:%M:%S}",
                   '24:00:00',
                   # output filename and path
                   self.filename]

        return command

    def do_recording(self):
        self.active = True
        print(f"{self.url=} {self.duration_min=}")
        self.starttime = time.time()

        # start recording process
        self.process = subprocess.Popen(self.get_ffmpeg_call, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        universal_newlines=True)
        self.stderr_thread = Thread(target=self.output_handler, args=(self.process, 'stderr'))
        self.stderr_thread.daemon = True
        self.stderr_thread.start()

        while True:
            self.runtime_sec = (time.time() - self.starttime)
            if self.log:
                print(f"{self.schedule_id} # {self.runtime_sec=:02.1f} - {self.log[-1]}")
            else:
                print(f"{self.schedule_id} # {self.runtime_sec=:02.1f} - ")

            if self.runtime_sec > self.duration_min * 60:
                break
            time.sleep(2)

        self.end_recording()
        self.stderr_thread.join()

    def end_recording(self):
        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()
        self.active = False
        self.is_completed = True

    def output_handler(self, process, handler_type):
        for line in iter(process.stderr.readline, ''):
            self.log.append(line.strip())



def validate_unique_filename(filepath):
    path = Path(filepath)

    if not path.exists():
        return str(path)

    base_directory = path.parent
    base_filename = path.stem
    extension = path.suffix

    counter = 1
    new_filepath = path

    while new_filepath.exists():
        new_filename = f"{base_filename}_{counter}{extension}"
        new_filepath = base_directory / new_filename
        counter += 1

    return str(new_filepath)


if __name__ == '__main__':
    t = (5, 'RSH', '2023-06-18 10:24:07.765897', 1, None, 0, 0, 0, '2023-06-18 08:24:07', 'Radio Schleswig Holstein',
         'https://streams.rsh.de/rsh-live/aac-64')
    t2 = (2, 'LOS40', '2023-06-18 11:16:49.248646', 1, None, 0, 0, 0, '2023-06-18 08:16:49', 'LOS 40',
          'https://playerservices.streamtheworld.com/api/livestream-redirect/LOS40.mp3')

    recording_threads = []
    f = FFMPEGStreamRecording(schedule_id=t[0], duration_min=t[3], url=t[10])
    f.recording_thread.start()
    recording_threads.append(f)
    t = t2
    f = FFMPEGStreamRecording(schedule_id=t[0], duration_min=t[3], url=t[10])
    f.recording_thread.start()
    recording_threads.append(f)
    for f in recording_threads:
        f.recording_thread.join()
    print('Done')
