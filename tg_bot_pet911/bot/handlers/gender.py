from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from tg_bot_pet911.app.models import PetInfo
from tg_bot_pet911.keyboards.inline import get_photos_keyboard
from tg_bot_pet911.states.pet_states import PetRegistration


router = Router()


@router.callback_query(PetRegistration.selecting_gender, F.data.startswith("gender:"))
async def process_gender_selection(callback: CallbackQuery, state: FSMContext):
    """Process pet gender selection."""
    # Extract gender from callback data
    gender = callback.data.split(":")[-1]
    
    # Get current state data
    data = await state.get_data()
    
    # Update pet_info with the gender
    pet_info_dict = data.get("pet_info", {})
    pet_info_dict["gender"] = gender
    
    # Save updated pet_info back to state
    await state.update_data(pet_info=pet_info_dict)
    
    # Map to human-readable gender
    gender_text = {
        "male": "♂️ мальчика",
        "female": "♀️ девочку",
        "unknown": "питомца (пол неизвестен)"
    }
    
    pet_type = {
        "dog": "собаку",
        "cat": "кошку",
        "other": "животное"
    }
    
    await callback.message.edit_text(
        f"Вы нашли {pet_type.get(pet_info_dict.get('pet_type', 'other'), 'животное')} - "
        f"{gender_text.get(gender, 'неизвестно')}.\n\n"
        f"Теперь отправьте фото питомца. Вы можете отправить до 5 фото.\n"
        f"Когда закончите загрузку фото, нажмите 'Завершить загрузку'.",
        reply_markup=get_photos_keyboard()
    )
    
    # Move to the next state
    await state.set_state(PetRegistration.uploading_photos)
    await callback.answer()


@router.callback_query(PetRegistration.selecting_gender, F.data == "back")
async def back_to_pet_type(callback: CallbackQuery, state: FSMContext):
    """Return to pet type selection."""
    from tg_bot_pet911.keyboards.inline import get_pet_type_keyboard
    
    await callback.message.edit_text(
        "Какое животное вы нашли?",
        reply_markup=get_pet_type_keyboard()
    )
    
    # Set state back to pet type selection
    await state.set_state(PetRegistration.selecting_type)
    await callback.answer() 