# coding=utf-8
"""
Notification wrapper
"""
import notify2

from pyjoplin.configuration import config


# Start notification service for pyjoplin
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
    notification.show()


def show_error(summary, note_title='', message=''):
    show("ERROR: %s" % summary, note_title, message)


def show_error_and_raise(summary, note_title='', message=''):
    show_error(summary, note_title, message)
    raise Exception(summary)
