from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tg_bot_pet911.app.models import PetLocation
from tg_bot_pet911.keyboards.inline import get_photos_keyboard, get_location_keyboard
from tg_bot_pet911.states.pet_states import PetRegistration


router = Router()


@router.callback_query(PetRegistration.entering_location, F.data == "location:geo")
async def process_geo_location_request(callback: CallbackQuery, state: FSMContext):
    """Handle request to send geolocation."""
    await callback.message.edit_text(
        "📍 Пожалуйста, отправьте геопозицию, где вы нашли питомца.\n\n"
        "Для этого нажмите на скрепку (📎) в меню ввода и выберите 'Геопозиция'.\n"
        "Или введите /cancel для отмены."
    )
    # We stay in the same state, but expect a location message
    await callback.answer()


@router.message(PetRegistration.entering_location, F.location)
async def process_geo_location(message: Message, state: FSMContext):
    """Handle geolocation message."""
    # Get current state data
    data = await state.get_data()
    pet_info_dict = data.get("pet_info", {})
    
    # Create location object
    location = PetLocation(
        latitude=message.location.latitude,
        longitude=message.location.longitude
    )
    
    # Update pet_info with location
    if "location" not in pet_info_dict:
        pet_info_dict["location"] = {}
    
    pet_info_dict["location"] = location.model_dump()
    
    # Save updated pet_info back to state
    await state.update_data(pet_info=pet_info_dict)
    
    # Move to comment step
    await message.answer(
        "✅ Геопозиция сохранена!\n\n"
        "Теперь добавьте комментарий о питомце: особые приметы, поведение, наличие ошейника и т.д.\n"
        "Или напишите 'нет', если комментариев нет."
    )
    
    # Set state to entering comment
    await state.set_state(PetRegistration.entering_comment)


@router.callback_query(PetRegistration.entering_location, F.data == "location:manual")
async def process_manual_location_request(callback: CallbackQuery, state: FSMContext):
    """Handle request to manually enter location."""
    await callback.message.edit_text(
        "🏙️ Пожалуйста, введите адрес, где вы нашли питомца.\n\n"
        "Например: Москва, ул. Пушкина, д. 10"
    )
    # We stay in the same state, but expect a text message with address
    await callback.answer()


@router.message(PetRegistration.entering_location, F.text)
async def process_manual_location(message: Message, state: FSMContext):
    """Handle manual address entry."""
    address = message.text.strip()
    
    if not address:
        await message.answer(
            "⚠️ Пожалуйста, введите корректный адрес.\n"
            "Или вернитесь назад, чтобы выбрать другой способ указания местоположения."
        )
        return
    
    # Get current state data
    data = await state.get_data()
    pet_info_dict = data.get("pet_info", {})
    
    # Create location object
    location = PetLocation(address=address)
    
    # Update pet_info with location
    if "location" not in pet_info_dict:
        pet_info_dict["location"] = {}
    
    pet_info_dict["location"] = location.model_dump()
    
    # Save updated pet_info back to state
    await state.update_data(pet_info=pet_info_dict)
    
    # Move to comment step
    await message.answer(
        f"✅ Адрес '{address}' сохранен!\n\n"
        f"Теперь добавьте комментарий о питомце: особые приметы, поведение, наличие ошейника и т.д.\n"
        f"Или напишите 'нет', если комментариев нет."
    )
    
    # Set state to entering comment
    await state.set_state(PetRegistration.entering_comment)


@router.callback_query(PetRegistration.entering_location, F.data == "back")
async def back_to_photos(callback: CallbackQuery, state: FSMContext):
    """Return to photo upload."""
    # Get current state data
    data = await state.get_data()
    pet_info_dict = data.get("pet_info", {})
    
    # Clear location if it was set
    if "location" in pet_info_dict:
        pet_info_dict["location"] = {}
        await state.update_data(pet_info=pet_info_dict)
    
    # Move back to photo upload
    await callback.message.edit_text(
        "📸 Загрузите фото питомца.\n"
        "Вы можете отправить до 5 фото. Когда закончите, нажмите 'Завершить загрузку'.",
        reply_markup=get_photos_keyboard()
    )
    
    # Set state back to uploading photos
    await state.set_state(PetRegistration.uploading_photos)
    await callback.answer() 