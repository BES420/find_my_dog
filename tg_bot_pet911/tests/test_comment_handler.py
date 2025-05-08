import pytest
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tg_bot_pet911.bot.handlers.comment import process_comment, back_to_location
from tg_bot_pet911.states.pet_states import PetRegistration
from tg_bot_pet911.app.models import PetInfo, PetLocation


@pytest.mark.asyncio
async def test_process_comment(mock_message, mock_state):
    """Test the comment processing handler."""
    # Setup comment in message
    mock_message.text = "Это очень красивый пес, дружелюбный, отзывается на Шарик"
    
    # Setup mock state data
    pet_info = PetInfo(
        user_id=mock_message.from_user.id,
        chat_id=mock_message.chat.id,
        username=mock_message.from_user.username,
        pet_type="dog",
        gender="male"
    )
    pet_info.location = PetLocation(latitude=55.753215, longitude=37.622504)
    
    mock_state.get_data.return_value = {
        "pet_info": pet_info.model_dump()
    }
    
    # Execute handler
    await process_comment(mock_message, mock_state)
    
    # Verify state data was updated
    mock_state.update_data.assert_called_once()
    
    # Verify state was updated to next state
    mock_state.set_state.assert_called_once_with(PetRegistration.confirming)
    
    # Verify message was sent
    mock_message.answer.assert_called_once()
    answer_args = mock_message.answer.call_args[0][0]
    assert "объявление" in answer_args.lower()


@pytest.mark.asyncio
async def test_back_to_location(mock_callback_query, mock_state):
    """Test the back to location handler."""
    # Setup callback data
    mock_callback_query.data = "back"
    
    # Setup mock state data
    pet_info = PetInfo(
        user_id=mock_callback_query.from_user.id,
        chat_id=mock_callback_query.message.chat.id,
        username=mock_callback_query.from_user.username,
        pet_type="dog",
        gender="male"
    )
    pet_info.location = PetLocation(latitude=55.753215, longitude=37.622504)
    
    mock_state.get_data.return_value = {
        "pet_info": pet_info.model_dump()
    }
    
    # Execute handler
    await back_to_location(mock_callback_query, mock_state)
    
    # Verify state was updated to previous state
    mock_state.set_state.assert_called_once_with(PetRegistration.entering_location)
    
    # Verify message was edited
    mock_callback_query.message.edit_text.assert_called_once()
    edit_text_args = mock_callback_query.message.edit_text.call_args[0][0]
    assert "где вы нашли" in edit_text_args.lower()
    
    # Verify callback was answered
    mock_callback_query.answer.assert_called_once() 