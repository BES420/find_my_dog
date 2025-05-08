import pytest
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot_pet911.bot.handlers.cancel import cmd_cancel


@pytest.mark.asyncio
async def test_cmd_cancel(mock_message, mock_state):
    """Test the cancel command handler."""
    # Execute handler
    await cmd_cancel(mock_message, mock_state)
    
    # Verify state was cleared
    mock_state.clear.assert_called_once()
    
    # Verify message was sent
    mock_message.answer.assert_called_once()
    answer_args = mock_message.answer.call_args[0][0]
    assert "отменена" in answer_args.lower() 