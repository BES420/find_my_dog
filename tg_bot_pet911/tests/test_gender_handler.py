import pytest
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from tg_bot_pet911.bot.handlers.gender import process_gender_selection
from tg_bot_pet911.states.pet_states import PetRegistration
from tg_bot_pet911.app.models import PetInfo


@pytest.mark.asyncio
async def test_process_gender_selection(mock_callback_query, mock_state):
    """Test the gender selection handler."""
    # Setup callback data
    mock_callback_query.data = "gender:male"
    
    # Setup mock state data
    pet_info = PetInfo(
        user_id=mock_callback_query.from_user.id,
        chat_id=mock_callback_query.message.chat.id,
        username=mock_callback_query.from_user.username,
        pet_type="dog",
        gender=""
    )
    
    mock_state.get_data.return_value = {
        "pet_info": pet_info.model_dump()
    }
    
    # Execute handler
    await process_gender_selection(mock_callback_query, mock_state)
    
    # Verify that state data was updated
    mock_state.update_data.assert_called_once()
    
    # Verify state was updated to next state
    mock_state.set_state.assert_called_once_with(PetRegistration.uploading_photos)
    
    # Verify message was edited
    mock_callback_query.message.edit_text.assert_called_once()
    edit_text_args = mock_callback_query.message.edit_text.call_args[0][0]
    assert "нашли" in edit_text_args
    assert "фото" in edit_text_args
    
    # Verify callback was answered
    mock_callback_query.answer.assert_called_once() 