# Python Web Radio Recorder (PyWRR)

Self hosted, raspberry pi friendly project to automatically
record web radio 📻 using FFMPEG.

Currently not much more than a prototype.


## Design decisions:

- Targets an audience who understands what a stream URL of a web radio station is and how to find it.
- Use Flask & HTMX because it's easy
- Use a local sqlite3 database to store scheduling data
- Use FFMPEG to capture streams (but be open to other tools, should they be required)
- It's not necessary to be exactly on time - later recordings will have automatic pre/post roll
- Needs mobile friendly web interface. Use nginx to protect the service
- As an exercise in laziness the sql functionality is mostly written using ChatGPT


## TODO
- first attempt on a web site

                    

                    
