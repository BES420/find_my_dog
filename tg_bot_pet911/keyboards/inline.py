from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_pet_type_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting pet type."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🐶 Собака", callback_data="pet_type:dog"),
        InlineKeyboardButton(text="🐱 Кошка", callback_data="pet_type:cat"),
    )
    builder.row(
        InlineKeyboardButton(text="🐾 Другое", callback_data="pet_type:other"),
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
    )
    return builder.as_markup()


def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting pet gender."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="♂️ Мальчик", callback_data="gender:male"),
        InlineKeyboardButton(text="♀️ Девочка", callback_data="gender:female"),
    )
    builder.row(
        InlineKeyboardButton(text="❓ Не знаю", callback_data="gender:unknown"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
    )
    return builder.as_markup()


def get_location_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for entering location."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📍 Отправить геопозицию", callback_data="location:geo"),
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Ввести адрес вручную", callback_data="location:manual"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
    )
    return builder.as_markup()


def get_photos_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for photo uploading completion."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Завершить загрузку", callback_data="photos:done"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
    )
    return builder.as_markup()


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for final confirmation."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm:yes"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="confirm:no"),
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Начать заново", callback_data="confirm:restart"),
    )
    return builder.as_markup() 