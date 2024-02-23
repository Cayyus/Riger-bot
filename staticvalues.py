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

statuses = ['100000 people', 'Youtube', 'way too many people', 'Twitch', 'Fortnite streams', 'MrBeast']
messages = cycle(statuses)

def timestamp_formatting(date):
    timestamp = datetime.fromisoformat(str(date))
    timestamp_formatted = int(timestamp.timestamp())
    return f"<t:{timestamp_formatted}:d>"



    
