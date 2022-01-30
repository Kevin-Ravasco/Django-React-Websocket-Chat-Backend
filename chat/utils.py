from django.core.exceptions import ObjectDoesNotExist

from chat.models import SingleChat


def get_users_chat(user, participant):
    # try to get the chat in reverse orders, create one if it does not exist
    try:
        chat = SingleChat.objects.get(participant1=user, participant2=participant)
    except ObjectDoesNotExist:
        try:
            chat = SingleChat.objects.get(participant1=participant, participant2=user)
        except ObjectDoesNotExist:
            chat = SingleChat.objects.create(participant1=user, participant2=participant)
    return chat