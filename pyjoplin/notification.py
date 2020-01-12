# coding=utf-8
"""
Notification wrapper
"""
import notify2
import os.path
import sys

from pyjoplin.configuration import config


# Start notification service for pyjoplin
if os.path.isfile(os.path.expanduser('~/var/pyjoplin/SKIP_NOTIFICATIONS')):
    # NOTE:
    # `mkdir -p ~/var/pyjoplin && touch ~/var/pyjoplin/SKIP_NOTIFICATIONS` to disable notifications
    # `rm ~/var/pyjoplin/SKIP_NOTIFICATIONS` to enable again
    print('Skipping notify2 setup because ~/var/pyjoplin/SKIP_NOTIFICATIONS exists', file=sys.stderr)
else:
    notify2.init("pyjoplin")


def show(summary, note_title='', message=''):
    if note_title:
        full_message = "Note: %s\n%s" % (note_title, message)
    else:
        full_message = message
    notification = notify2.Notification(
        summary,
        message=full_message,
        icon=config.PATH_ICON
    )
    try:
        notification.show()
    except notify2.UninittedError:
        print('Skipping notification because notify2.init() was not run successfully')


def show_error(summary, note_title='', message=''):
    show("ERROR: %s" % summary, note_title, message)


def show_error_and_raise(summary, note_title='', message=''):
    show_error(summary, note_title, message)
    raise Exception(summary)
