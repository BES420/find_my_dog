from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot_pet911.app.models import PetInfo
from tg_bot_pet911.keyboards.inline import get_pet_type_keyboard, get_gender_keyboard
from tg_bot_pet911.states.pet_states import PetRegistration


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command."""
    # Reset state to make sure we're starting clean
    await state.clear()
    
    await message.answer(
        "👋 Привет! Я бот для поиска потерянных питомцев.\n\n"
        "Чтобы создать объявление о найденном питомце, "
        "я задам несколько вопросов для сбора необходимой информации.\n\n"
        "Какое животное вы нашли?",
        reply_markup=get_pet_type_keyboard()
    )
    
    # Set state to selecting pet type
    await state.set_state(PetRegistration.selecting_type)


@router.callback_query(PetRegistration.selecting_type, F.data.startswith("pet_type:"))
async def process_pet_type(callback: CallbackQuery, state: FSMContext):
    """Process pet type selection."""
    # Extract pet type from callback data
    pet_type = callback.data.split(":")[-1]
    
    # Save to state
    await state.update_data(pet_type=pet_type)
    
    # Create initial PetInfo object
    user = callback.from_user
    pet_info = PetInfo(
        user_id=user.id,
        chat_id=callback.message.chat.id,
        username=user.username,
        pet_type=pet_type,
        gender=""  # Will be filled in next step
    )
    
    # Save to state
    await state.update_data(pet_info=pet_info.model_dump())
    
    # Edit message to avoid cluttering the chat
    pet_types = {
        "dog": "🐶 Собаку",
        "cat": "🐱 Кошку",
        "other": "🐾 Другое животное"
    }
    
    await callback.message.edit_text(
        f"Вы нашли {pet_types.get(pet_type, 'неизвестное животное')}.\n\n"
        f"Теперь укажите пол животного.",
        reply_markup=get_gender_keyboard()
    )
    
    # Update state
    await state.set_state(PetRegistration.selecting_gender)
    
    # Answer callback to remove loading state
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def process_cancel(callback: CallbackQuery, state: FSMContext):
    """Cancel the current operation."""
    await state.clear()
    await callback.message.edit_text(
        "❌ Операция отменена. Чтобы начать снова, используйте команду /start."
    )
    await callback.answer() 