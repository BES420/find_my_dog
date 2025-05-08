from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tg_bot_pet911.app.models import PetInfo
from tg_bot_pet911.keyboards.inline import get_confirmation_keyboard, get_location_keyboard
from tg_bot_pet911.states.pet_states import PetRegistration


router = Router()


@router.message(PetRegistration.entering_comment)
async def process_comment(message: Message, state: FSMContext):
    """Process comment input."""
    # Get comment text
    comment = message.text.strip()
    
    # Handle "нет" as no comment
    if comment.lower() == "нет":
        comment = ""
    
    # Get current state data
    data = await state.get_data()
    pet_info_dict = data.get("pet_info", {})
    
    # Update pet_info with comment
    pet_info_dict["comment"] = comment
    
    # Save updated pet_info back to state
    await state.update_data(pet_info=pet_info_dict)
    
    # Create a PetInfo object to format the preview
    pet_info = PetInfo(**pet_info_dict)
    
    # Format a preview of the announcement
    preview_text = pet_info.format_for_publication()
    
    # Send confirmation with preview
    await message.answer(
        "📝 Вот как будет выглядеть ваше объявление:\n\n"
        f"{preview_text}\n\n"
        "Всё верно?",
        reply_markup=get_confirmation_keyboard()
    )
    
    # Set state to confirming
    await state.set_state(PetRegistration.confirming)


@router.callback_query(PetRegistration.entering_comment, F.data == "back")
async def back_to_location(callback: CallbackQuery, state: FSMContext):
    """Return to location entry."""
    # Get current state data
    data = await state.get_data()
    pet_info_dict = data.get("pet_info", {})
    
    # Clear comment if it was set
    pet_info_dict["comment"] = ""
    await state.update_data(pet_info=pet_info_dict)
    
    # Move back to location input
    await callback.message.edit_text(
        "🌍 Укажите, где вы нашли питомца.\n\n"
        "Вы можете отправить геопозицию или ввести адрес вручную.",
        reply_markup=get_location_keyboard()
    )
    
    # Set state back to entering location
    await state.set_state(PetRegistration.entering_location)
    await callback.answer() 