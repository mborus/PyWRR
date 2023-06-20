# Python Web Radio Recorder (PyWRR)

Self hosted, raspberry pi friendly project to automatically
record web radio 📻 using FFMPEG.

🚧 this is just a barely working a prototype 🚧


## Design decisions:
- Targets an audience who understands what a stream URL of a web radio station is and how to find it.
- Targets an audience that can install FFMPEG, Python and requires Python skills to get up and running.
- Use Flask & HTMX because it's easy
- Use a local sqlite3 database to store scheduling data
- Use FFMPEG to capture streams (but be open to other tools, should they be required)
- It's not necessary to be exactly on time - later recordings will have automatic pre/post roll
- Needs mobile friendly web interface. Use nginx to protect the service
- Backend and frontend are seperated, so that scheduled recordings are not affected by front end problems
- As an exercise in laziness the sql and flask functionality is mostly outsourced to ChatGPT


## Tasks
- ✔️ FFMPEG recording of web radio
- ❌ alternative recording helpers (streamripper, etc)
- ❌ managing recordings, monitoring space
- ❌ saving recordings at a suitable location
- ⚠️ authentification (outsourced to nginx)
- ❌ setup
- ✔️ basic "wireframe" web site 
- ❌ fix browser back button navigation
- ✔️ managing radio station urls
- ✔️ basic scheduling
- ❌ changing recordings that are running
- ✔️ downloading completed recordings
- ❌ live streaming recordings in progress with navigation
- ❌ tests
                    
## Requirements
- local FFMPEG installation on the path
- Python 3.11.x, venv according to requirements.txt 

## Installation
- Install FFMPEG requirement
- Run both "app.py" and "scheduler.py" as seperated tasks

👉🏼 If you're looking for a battle tested fremium service, there's https://www.phonostar.de/ (no relation)