import sys
import logging
import os
import datetime

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

userName = os.path.expanduser("~")
organizerFolder = os.path.join(userName, "Organizer")

os.makedirs(organizerFolder, exist_ok=True)