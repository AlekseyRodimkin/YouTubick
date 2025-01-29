from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    """Class of user states"""

    # youtube
    waiting_youtube_link = State()
