# TODO - check if this actually works
import os
import shutil
import ctypes

def get_free_space(folder):
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

folder_path = "/path/to/folder"  # Replace with the actual folder path
free_space = get_free_space(folder_path)

print(f"Free space in '{folder_path}': {free_space} bytes")