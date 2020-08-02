import urllib.parse
import inspect

from users.models import User

from linebot.models import (
    MessageEvent, PostbackEvent,
    PostbackAction,
    TextMessage, TextSendMessage, TemplateSendMessage,
    ButtonsTemplate, CarouselTemplate, CarouselColumn, QuickReply, QuickReplyButton,
)


"""Common bot specification classes
"""
class ActionHandler:
    actions = {}

    def add(self, action_name):
        def decorator(func):
            self.__add_action(action_name, func)
            return func
        return decorator

    def __add_action(self, action_name, func):
        self.actions[action_name] = func

    def get(self, action_name):
        return self.actions.get(action_name)


class Menu:
    title = None
    name = None

    def __init__(self):
        self.action_handler = ActionHandler()
        # 自身のメソッドを調べてアクションを追加する
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        for member in members:
            name = member[0]
            method = member[1]
            if name.startswith('action_'):
                action_name = name.replace('action_', '')
                self.action_handler.add(action_name)(method)

    def main_action(self, event):
        raise NotImplementedError
    
    def search_action(self, name):
        return self.action_handler.get(name)

    def get_hostess(self, event):
        line_user_id = event.source.user_id
        hostess = User.objects.get_hostess(line_user_id=line_user_id)
        return hostess
    
    def get_guest(self, event):
        line_user_id = event.source.user_id
        guest = User.objects.get_guest(line_user_id=line_user_id)
        return guest


class MenuHandler:
    menus = {}
    menus_by_name = {}

    def add(self, instance):
        title = instance.title
        name = instance.name
        self.menus[title] = instance
        self.menus_by_name[name] = instance
    
    def search_menu(self, name):
        return self.menus.get(name)

    def get_menu(self, name):
        return self.menus_by_name.get(name)


"""Utilities
"""
def reverse(instance, action):
    for name, method in instance.action_handler.actions.items():
        if action == method:
            return name

def first(l):
    if len(l) > 0:
        return l[0]
    return None

def parse_query(query_string):
    query = {}
    qs = urllib.parse.parse_qs(query_string)
    for k, v in qs.items():
        query[k] = first(v)
    return query


"""Message Packages
"""
def SimpleMenu(instance, actions={}):
    actions = [
        PostbackAction(
            label=text,
            display_text=text,
            data='menu={}&action={}'.format(instance.name, reverse(instance, action))
        )
        for action, text in actions.items()
    ]
    buttons = ButtonsTemplate(text='選択してください', title='{}メニュー'.format(instance.title), actions=actions)
    message = TemplateSendMessage(alt_text='alt text', template=buttons)
    return message


def SimpleSelection(instance, title='', action='', answers=[]):
    items = [
        QuickReplyButton(
            action=PostbackAction(
                label=answer['text'],
                data='menu={}&action={}&{}={}'.format(instance.name, action, answer['key'], answer['value']),
                display_text=answer['text']
            )
        )
        for answer in answers
    ]    
    message = TextSendMessage(text=title, quick_reply=QuickReply(items=items))
    return message


def SimpleSelectionItem(text='', key=None, value=None):
    return dict(text=text, key=key, value=value)