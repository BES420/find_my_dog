import pytest
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot_pet911.bot.handlers.start import cmd_start
from tg_bot_pet911.states.pet_states import PetRegistration


@pytest.mark.asyncio
async def test_cmd_start(mock_message, mock_state):
    """Test the start command handler."""
    # Execute handler
    await cmd_start(mock_message, mock_state)
    
    # Verify state was cleared
    mock_state.clear.assert_called_once()
    
    # Verify state was set
    mock_state.set_state.assert_called_once_with(PetRegistration.selecting_type)
    
    # Verify message was sent with keyboard
    mock_message.answer.assert_called_once()
    
    # Check message content - "питомцев" вместо "питомец"
    call_args = mock_message.answer.call_args[0][0]
    assert "Привет!" in call_args
    assert "питомц" in call_args
    assert "животное" in call_args


@pytest.mark.asyncio
async def test_process_pet_type(mock_callback_query, mock_state):
    """Test the pet type selection handler."""
    # Setup callback data
    mock_callback_query.data = "pet_type:dog"
    
    # Import here to avoid circular imports
    from tg_bot_pet911.bot.handlers.start import process_pet_type
    
    # Execute handler
    await process_pet_type(mock_callback_query, mock_state)
    
    # Verify data was saved to state
    mock_state.update_data.assert_called()
    
    # Verify state was updated
    mock_state.set_state.assert_called_once_with(PetRegistration.selecting_gender)
    
    # Verify message was edited
    mock_callback_query.message.edit_text.assert_called_once()
    
    # Verify callback was answered
    mock_callback_query.answer.assert_called_once()


@pytest.mark.asyncio
async def test_process_cancel(mock_callback_query, mock_state):
    """Test the cancel handler."""
    # Setup callback data
    mock_callback_query.data = "cancel"
    
    # Import here to avoid circular imports
    from tg_bot_pet911.bot.handlers.start import process_cancel
    
    # Execute handler
    await process_cancel(mock_callback_query, mock_state)
    
    # Verify state was cleared
    mock_state.clear.assert_called_once()
    
    # Verify message was edited
    mock_callback_query.message.edit_text.assert_called_once()
    edit_text_args = mock_callback_query.message.edit_text.call_args[0][0]
    assert "Операция отменена" in edit_text_args
    
    # Verify callback was answered
    mock_callback_query.answer.assert_called_once() 