import pytest
from unittest.mock import patch, MagicMock
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tg_bot_pet911.bot.handlers.confirm import confirm_submission, reject_submission, restart_submission
from tg_bot_pet911.states.pet_states import PetRegistration
from tg_bot_pet911.app.models import PetInfo, PetLocation, PetPhoto


@pytest.mark.asyncio
async def test_confirmation_view(mock_message, mock_state):
    """Test the confirmation view handler (using comment handler).
    
    This test uses the comment handler to test the confirmation view
    since that's what sets up the confirmation state.
    """
    # Setup mock message
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
    pet_info.photos = [PetPhoto(file_id="test_file_id", file_unique_id="test_file_unique_id")]
    
    mock_state.get_data.return_value = {
        "pet_info": pet_info.model_dump()
    }
    
    # Import the function here to avoid circular imports
    from tg_bot_pet911.bot.handlers.comment import process_comment
    
    # Execute handler
    await process_comment(mock_message, mock_state)
    
    # Verify message was sent
    mock_message.answer.assert_called()
    # We should get at least one call
    assert mock_message.answer.call_count >= 1


@pytest.mark.asyncio
async def test_confirm_submission(mock_callback_query, mock_state, mock_bot):
    """Test the confirmation handler."""
    # Setup callback data
    mock_callback_query.data = "confirm:yes"
    
    # Setup mock state data
    pet_info = PetInfo(
        user_id=mock_callback_query.from_user.id,
        chat_id=mock_callback_query.message.chat.id,
        username=mock_callback_query.from_user.username,
        pet_type="dog",
        gender="male",
        comment="Это очень красивый пес"  # Добавляем строковый comment
    )
    pet_info.location = PetLocation(latitude=55.753215, longitude=37.622504)
    pet_info.photos = [PetPhoto(file_id="test_file_id", file_unique_id="test_file_unique_id")]
    
    mock_state.get_data.return_value = {
        "pet_info": pet_info.model_dump()
    }
    
    # Patch the functions that would be called
    with patch('tg_bot_pet911.bot.handlers.confirm.save_pet_data') as mock_save_pet_data:
        mock_save_pet_data.return_value = ("/path/to/save", {"test": "data"})
        
        with patch('tg_bot_pet911.bot.handlers.confirm.send_notification') as mock_send_notification:
            mock_send_notification.return_value = None
            
            # Execute handler
            await confirm_submission(mock_callback_query, mock_state, mock_bot)
            
            # Verify state was cleared
            mock_state.clear.assert_called_once()
            
            # Verify message was edited
            mock_callback_query.message.edit_text.assert_called_once()
            
            # Verify callback was answered
            mock_callback_query.answer.assert_called_once()


@pytest.mark.asyncio
async def test_reject_submission(mock_callback_query, mock_state):
    """Test the rejection handler."""
    # Setup callback data
    mock_callback_query.data = "confirm:no"
    
    # Execute handler
    await reject_submission(mock_callback_query, mock_state)
    
    # Verify state was cleared
    mock_state.clear.assert_called_once()
    
    # Verify message was edited
    mock_callback_query.message.edit_text.assert_called_once()
    edit_text_args = mock_callback_query.message.edit_text.call_args[0][0]
    assert "отменили" in edit_text_args
    
    # Verify callback was answered
    mock_callback_query.answer.assert_called_once()


@pytest.mark.asyncio
async def test_restart_submission(mock_callback_query, mock_state):
    """Test the restart handler."""
    # Setup callback data
    mock_callback_query.data = "confirm:restart"
    
    # Execute handler
    await restart_submission(mock_callback_query, mock_state)
    
    # Verify state was cleared
    mock_state.clear.assert_called_once()
    
    # Verify state was set to initial state
    mock_state.set_state.assert_called_once_with(PetRegistration.selecting_type)
    
    # Verify message was edited
    mock_callback_query.message.edit_text.assert_called_once()
    edit_text_args = mock_callback_query.message.edit_text.call_args[0][0]
    assert "Начинаем заново" in edit_text_args
    
    # Verify callback was answered
    mock_callback_query.answer.assert_called_once() 