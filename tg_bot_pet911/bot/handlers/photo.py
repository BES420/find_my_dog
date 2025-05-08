from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PhotoSize
from aiogram.fsm.context import FSMContext

from tg_bot_pet911.app.models import PetPhoto, PetInfo
from tg_bot_pet911.keyboards.inline import get_photos_keyboard, get_location_keyboard, get_gender_keyboard
from tg_bot_pet911.states.pet_states import PetRegistration
from tg_bot_pet911.config.config import MAX_PHOTOS


router = Router()


@router.message(PetRegistration.uploading_photos, F.photo)
async def process_photo_upload(message: Message, state: FSMContext):
    """Handle photo uploads."""
    # Get current state data
    data = await state.get_data()
    pet_info_dict = data.get("pet_info", {})
    
    # Get photo from message
    photo = message.photo[-1]  # Get the largest version of the photo
    
    # Create PetPhoto object
    pet_photo = PetPhoto(
        file_id=photo.file_id,
        file_unique_id=photo.file_unique_id
    )
    
    # Add to photos list in pet_info
    photos = pet_info_dict.get("photos", [])
    
    # Check if we've reached maximum photos
    if len(photos) >= MAX_PHOTOS:
        await message.answer(
            f"⚠️ Вы уже загрузили максимальное количество фото ({MAX_PHOTOS}).\n"
            f"Нажмите 'Завершить загрузку', чтобы перейти к следующему шагу.",
            reply_markup=get_photos_keyboard()
        )
        return
    
    # Add new photo
    photos.append(pet_photo.model_dump())
    pet_info_dict["photos"] = photos
    
    # Save updated pet_info back to state
    await state.update_data(pet_info=pet_info_dict)
    
    # Send confirmation
    await message.answer(
        f"✅ Фото {len(photos)}/{MAX_PHOTOS} загружено!\n\n"
        f"Вы можете загрузить еще фото или нажать 'Завершить загрузку'.",
        reply_markup=get_photos_keyboard()
    )


@router.callback_query(PetRegistration.uploading_photos, F.data == "photos:done")
async def complete_photo_upload(callback: CallbackQuery, state: FSMContext):
    """Complete photo upload process."""
    # Get current state data
    data = await state.get_data()
    pet_info_dict = data.get("pet_info", {})
    
    # Check if at least one photo was uploaded
    photos = pet_info_dict.get("photos", [])
    if not photos:
        await callback.answer("⚠️ Необходимо загрузить хотя бы одно фото питомца!", show_alert=True)
        return
    
    # Move to location step
    await callback.message.edit_text(
        "🌍 Теперь укажите, где вы нашли питомца.\n\n"
        "Вы можете отправить геопозицию или ввести адрес вручную.",
        reply_markup=get_location_keyboard()
    )
    
    # Set state to entering location
    await state.set_state(PetRegistration.entering_location)
    await callback.answer()


@router.callback_query(PetRegistration.uploading_photos, F.data == "back")
async def back_to_gender(callback: CallbackQuery, state: FSMContext):
    """Return to gender selection."""
    # Get current state data
    data = await state.get_data()
    pet_info_dict = data.get("pet_info", {})
    
    # Clear any photos that might have been uploaded
    pet_info_dict["photos"] = []
    await state.update_data(pet_info=pet_info_dict)
    
    # Move back to gender selection
    await callback.message.edit_text(
        "Укажите пол питомца:",
        reply_markup=get_gender_keyboard()
    )
    
    # Set state back to selecting gender
    await state.set_state(PetRegistration.selecting_gender)
    await callback.answer() 