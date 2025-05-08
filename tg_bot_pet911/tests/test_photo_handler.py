import pytest
from unittest.mock import MagicMock
from aiogram.types import Message, PhotoSize
from aiogram.fsm.context import FSMContext

from tg_bot_pet911.bot.handlers.photo import process_photo_upload, complete_photo_upload
from tg_bot_pet911.states.pet_states import PetRegistration
from tg_bot_pet911.app.models import PetInfo


@pytest.mark.asyncio
async def test_process_photo(mock_message, mock_state):
    """Test the photo processing handler."""
    # Setup photo in message
    photo_size = MagicMock(spec=PhotoSize)
    photo_size.file_id = "test_file_id"
    photo_size.file_unique_id = "test_file_unique_id"
    mock_message.photo = [photo_size]
    
    # Setup mock state data
    pet_info = PetInfo(
        user_id=mock_message.from_user.id,
        chat_id=mock_message.chat.id,
        username=mock_message.from_user.username,
        pet_type="dog",
        gender="male"
    )
    
    mock_state.get_data.return_value = {
        "pet_info": pet_info.model_dump()
    }
    
    # Execute handler
    await process_photo_upload(mock_message, mock_state)
    
    # Verify state data was updated
    mock_state.update_data.assert_called_once()
    
    # Verify message was sent
    mock_message.answer.assert_called_once()
    answer_args = mock_message.answer.call_args[0][0]
    assert "Фото" in answer_args
    assert "загружено" in answer_args


@pytest.mark.asyncio
async def test_process_photos_done(mock_callback_query, mock_state):
    """Test the photos done handler."""
    # Setup callback data
    mock_callback_query.data = "photos:done"
    
    # Setup mock state data
    pet_info = PetInfo(
        user_id=mock_callback_query.from_user.id,
        chat_id=mock_callback_query.message.chat.id,
        username=mock_callback_query.from_user.username,
        pet_type="dog",
        gender="male"
    )
    pet_info.photos = [{"file_id": "test_file_id", "file_unique_id": "test_file_unique_id"}]
    
    mock_state.get_data.return_value = {
        "pet_info": pet_info.model_dump()
    }
    
    # Execute handler
    await complete_photo_upload(mock_callback_query, mock_state)
    
    # Verify state was updated to next state
    mock_state.set_state.assert_called_once_with(PetRegistration.entering_location)
    
    # Verify message was edited
    mock_callback_query.message.edit_text.assert_called_once()
    edit_text_args = mock_callback_query.message.edit_text.call_args[0][0]
    assert "геопозицию" in edit_text_args
    assert "адрес" in edit_text_args
    
    # Verify callback was answered
    mock_callback_query.answer.assert_called_once() 