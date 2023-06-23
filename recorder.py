import time
from threading import Thread
import subprocess
from pathlib import Path
from settings import RECORDING_PATH

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
        if self.filename is None:
            raise ValueError('Filename for recording not given.')

        recording_path = Path(RECORDING_PATH, self.filename)


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
                   recording_path]

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
            self.runtime_sec = int(time.time() - self.starttime)
            remaining_sec = self.duration_min * 60 - self.runtime_sec
            print(f"[#{self.schedule_id}:{remaining_sec}s] {self.runtime_sec=:02.1f} - {self.log[-1] if self.log else '-'}")
            if remaining_sec <= 0:
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


