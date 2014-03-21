__all__ = (
    'add_message_for', 'broadcast_message',
    'mark_read', 'mark_all_read',
)

from django.db import transaction
from .models import Message, MessageArchive, Inbox


def add_message_for(users, level, message, extra_tags='', fail_silently=False, **kwargs):
    """
    Send a message to a list of users without passing through `django.contrib.messages`

    :param users: an iterable containing the recipients of the messages
    :param level: message level
    :param message: the string containing the message
    :param extra_tags: like the Django api, a string containing extra tags for the message
    :param fail_silently: not used at the moment
    """
    # set up the base fields used to create the message
    message_fields = {
        'message': message,
        'level': level,
        'tags': extra_tags
    }
    #
    # We have the JSONField installed and available
    #
    if 'data' in Message._meta.get_all_field_names():
        # we have it *yay* so add our kwargs
        message_fields.update({
            'data': kwargs
        })

    with transaction.atomic():
        m = Message.objects.create(**message_fields)

        for u in users:
            MessageArchive.objects.create(user=u, message=m)
            Inbox.objects.create(user=u, message=m)


def broadcast_message(level, message, extra_tags='', fail_silently=False):
    """
    Send a message to all users in the system. TODO.
    """
    # TODO
    raise NotImplementedError


def mark_read(user, message):
    """
    Mark message instance as read for user.
    Returns True if the message was `unread` and thus actually marked as `read` or False in case
    it is already `read` or it does not exist at all.

    :param user: user instance for the recipient
    :param message: a Message instance to mark as read
    """
    try:
        inbox_m = Inbox.objects.filter(user=user, message=message).get()
        inbox_m.delete()
        return True
    except Inbox.DoesNotExist:
        return False


def mark_all_read(user):
    """
    Mark all message instances for a user as read.

    :param user: user instance for the recipient
    """
    with transaction.atomic():
        Inbox.objects.filter(user=user).delete()
