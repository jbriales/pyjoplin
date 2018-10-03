# coding=utf-8
"""
Notification wrapper
"""
import notify2

from pyjoplin.configuration import config


# Start notification service for pyjoplin
notify2.init("pyjoplin")


def show(summary, message=''):
    notification = notify2.Notification(
        summary,
        message=message,
        icon=config.PATH_ICON
    )
    notification.show()


def show_error(summary, message=''):
    show("ERROR: %s" % summary, message)


def show_error_and_raise(summary, message=''):
    show_error(summary, message)
    raise Exception(summary)
