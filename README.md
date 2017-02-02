# Reddit Background Downloader

Defaults to downloading from /r/EarthPorn.

Designed for Ubuntu 16.04.
Currently supports GNOME, Unity, and MATE on Linux.

Plasma Desktop, Windows, and possibly macOS support planned.

If you're running on Ubuntu 16.04, first install the system dependencies:

    $ sudo apt install python3-gi gir1.2-glib-2.0 gir1.2-gtk-3.0 gir1.2-notify-0.7 gir1.2-appindicator3-0.1

Then, optionally create a virtual environment to run in, and install `pip` dependencies:

    $ virtualenv -p python3 --prompt '(reddit-backgrounds) ' venv
    $ source venv/bin/activate
    (reddit-backgrounds) $ pip install -r requirements.txt
    
Now, the program can be run:

    $ ./reddit-backgrounds.py
