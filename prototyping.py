
import os
from pathlib import Path
import shutil
import ctypes
from recorder import FFMPEGStreamRecording
from settings import RECORDING_PATH

def get_free_space(folder):
    # TODO - check if this actually works
    if os.name == "posix":  # Linux
        stat = os.statvfs(folder)
        return stat.f_bavail * stat.f_frsize
    elif os.name == "nt":  # Windows
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            folder,
            None,
            None,
            ctypes.pointer(free_bytes)
        )
        return free_bytes.value
    else:
        raise OSError("Unsupported operating system")


def prototype_show_free_space(folder_path):
    free_space = get_free_space(folder_path)
    print(f"Free space in '{folder_path}': {free_space} bytes")


def prototype_2_recordings():
    t = (5, 'RSH', '2023-06-18 10:24:07.765897', 1, None, 0, 0, 0, '2023-06-18 08:24:07', 'Radio Schleswig Holstein',
         'https://streams.rsh.de/rsh-live/aac-64')
    t2 = (2, 'LOS40', '2023-06-18 11:16:49.248646', 1, None, 0, 0, 0, '2023-06-18 08:16:49', 'LOS 40',
          'https://playerservices.streamtheworld.com/api/livestream-redirect/LOS40.mp3')

    recording_threads = []
    f = FFMPEGStreamRecording(schedule_id=t[0], duration_min=t[3], url=t[10])
    f.filename = 'rec1a.ts'
    f.recording_thread.start()
    recording_threads.append(f)
    t = t2
    f = FFMPEGStreamRecording(schedule_id=t[0], duration_min=t[3], url=t[10])
    f.filename =  'rec2a.ts'
    f.recording_thread.start()
    recording_threads.append(f)
    for f in recording_threads:
        f.recording_thread.join()
    print('Done')


if __name__ == '__main__':
    prototype_2_recordings()




