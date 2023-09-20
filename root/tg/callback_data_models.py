from aiogram.filters.callback_data import CallbackData


class ActivityLevelCallback(CallbackData, prefix="activity_level"):
    index: float


class ChooseGenderCallback(CallbackData, prefix="choose_gender"):
    additional_value: int
    gender: str
    