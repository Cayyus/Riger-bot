from itertools import cycle
from datetime import datetime

badge_name_id = {
    'hypesquad_bravery': 1158402929728950282,
    'hypesquad_brilliance': 1158402984716288120,
    'hypesquad_balance': 1158403034133561364,
    'discord_nitro': 1158403082359677129,
    'discord_early_supporter': 1158403058846416947,
    'active_developer': 1158403009315880970
}

status_emotes = {
    'online': 1162244870052782102,
    'dnd': 1162245839343865926,
    'offline': 1162245242674753596,
    'idle': 1162244916932521984
}

trivia_categories = [
    {"name": 'Pick random categories', 'value': 'random'},
    {'name': 'General Knowledge', 'value': '9'},
    {'name': 'Books', 'value': '10'},
    {'name': 'Film', 'value': '11'},
    {'name': 'Music', 'value': '12'},
    {'name': 'Musicals & Theatres', 'value': '13'},
    {'name': 'Television', 'value': '14'},
    {'name': 'Video Games', 'value': '15'},
    {'name': 'Board Games', 'value': '16'},
    {'name': 'Nature', 'value': '17'},
    {'name': 'Computers', 'value': '18'},
    {'name': 'Mathematics', 'value': '19'},
    {'name': 'Mythology', 'value': '20'},
    {'name': 'Sports', 'value': '21'},
    {'name': 'Geography', 'value': '22'},
    {'name': 'History', 'value': '23'},
    {'name': 'Politics', 'value': '24'},
    {'name': 'Art', 'value': '25'},
    {'name': 'Celebrities', 'value': '26'},
    {'name': 'Animals', 'value': '27'},
    {'name': 'Vehicles', 'value': '28'},
    {'name': 'Comics', 'value': '29'},
    {'name': 'Gadgets', 'value': '30'},
    {'name': 'Anime & Manga', 'value': '31'},
    {'name': 'Cartoon & Animations', 'value': '32'}
]

statuses = ['100000 people', 'Youtube', 'way too many people', 'Twitch', 'Fortnite streams', 'MrBeast']
messages = cycle(statuses)

def timestamp_formatting(date):
    timestamp = datetime.fromisoformat(str(date))
    timestamp_formatted = int(timestamp.timestamp())
    return f"<t:{timestamp_formatted}:d>"
