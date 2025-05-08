import pytest
from unittest.mock import MagicMock
from aiogram.types import Message, Location, CallbackQuery
from aiogram.fsm.context import FSMContext

from tg_bot_pet911.bot.handlers.location import process_geo_location, process_manual_location, back_to_photos
from tg_bot_pet911.states.pet_states import PetRegistration
from tg_bot_pet911.app.models import PetInfo


@pytest.mark.asyncio
async def test_process_location(mock_message, mock_state):
    """Test the geo location processing handler."""
    # Setup location in message
    location = MagicMock(spec=Location)
    location.latitude = 55.753215
    location.longitude = 37.622504
    mock_message.location = location
    
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
    await process_geo_location(mock_message, mock_state)
    
    # Verify state data was updated
    mock_state.update_data.assert_called_once()
    
    # Verify state was updated to next state
    mock_state.set_state.assert_called_once_with(PetRegistration.entering_comment)
    
    # Verify message was sent
    mock_message.answer.assert_called_once()
    answer_args = mock_message.answer.call_args[0][0]
    assert "геопозиция" in answer_args.lower()


@pytest.mark.asyncio
async def test_process_address(mock_message, mock_state):
    """Test the address processing handler."""
    # Setup address in message
    mock_message.text = "Москва, Красная площадь, 1"
    
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
    await process_manual_location(mock_message, mock_state)
    
    # Verify state data was updated
    mock_state.update_data.assert_called_once()
    
    # Verify state was updated to next state
    mock_state.set_state.assert_called_once_with(PetRegistration.entering_comment)
    
    # Verify message was sent
    mock_message.answer.assert_called_once()
    answer_args = mock_message.answer.call_args[0][0]
    assert "адрес" in answer_args.lower()


@pytest.mark.asyncio
async def test_back_to_photos(mock_callback_query, mock_state):
    """Test the back to photos handler."""
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
    
    mock_state.get_data.return_value = {
        "pet_info": pet_info.model_dump()
    }
    
    # Execute handler
    await back_to_photos(mock_callback_query, mock_state)
    
    # Verify state was updated to previous state
    mock_state.set_state.assert_called_once_with(PetRegistration.uploading_photos)
    
    # Verify message was edited
    mock_callback_query.message.edit_text.assert_called_once()
    edit_text_args = mock_callback_query.message.edit_text.call_args[0][0]
    assert "фото" in edit_text_args.lower()
    
    # Verify callback was answered
    mock_callback_query.answer.assert_called_once() 