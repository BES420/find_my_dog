from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel current operation and clear state."""
    # Check if there's an active state
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer(
            "🤔 Нечего отменять. Используйте /start, чтобы начать создание объявления."
        )
        return
    
    # Clear state
    await state.clear()
    
    await message.answer(
        "❌ Операция отменена. Все введенные данные удалены.\n\n"
        "Используйте /start, чтобы начать создание объявления заново."
    ) 