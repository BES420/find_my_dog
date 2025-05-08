import pytest
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from collections import deque
from typing import List, Dict, Any, Callable, Awaitable, Optional, Deque
from unittest.mock import AsyncMock, MagicMock

from tg_bot_pet911.config.config import BOT_TOKEN


class MockBot(Bot):
    """Mock bot for testing purposes."""
    def __init__(self, *args, **kwargs):
        kwargs["session"] = AiohttpSession()
        super().__init__(*args, **kwargs)
        self.sent_messages: Deque[Dict[str, Any]] = deque()
        
    async def send_message(self, *args, **kwargs):
        """Mock send_message method."""
        self.sent_messages.append(kwargs)
        mock_message = AsyncMock()
        mock_message.message_id = len(self.sent_messages)
        mock_message.chat.id = kwargs.get("chat_id")
        mock_message.text = kwargs.get("text")
        return mock_message

    async def edit_message_text(self, *args, **kwargs):
        """Mock edit_message_text method."""
        self.sent_messages.append(kwargs)
        mock_message = AsyncMock()
        mock_message.message_id = kwargs.get("message_id", len(self.sent_messages))
        mock_message.chat.id = kwargs.get("chat_id")
        mock_message.text = kwargs.get("text")
        return mock_message

    async def send_photo(self, *args, **kwargs):
        """Mock send_photo method."""
        self.sent_messages.append(kwargs)
        mock_message = AsyncMock()
        mock_message.message_id = len(self.sent_messages)
        mock_message.chat.id = kwargs.get("chat_id")
        return mock_message

    async def send_location(self, *args, **kwargs):
        """Mock send_location method."""
        self.sent_messages.append(kwargs)
        mock_message = AsyncMock()
        mock_message.message_id = len(self.sent_messages)
        mock_message.chat.id = kwargs.get("chat_id")
        return mock_message
        
    def last_message(self) -> Optional[Dict[str, Any]]:
        """Get the last sent message."""
        return self.sent_messages[-1] if self.sent_messages else None


@pytest.fixture
def event_loop():
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_bot():
    """Create a mock bot instance."""
    return MockBot(token=BOT_TOKEN or "mock_token")


@pytest.fixture
def dp(mock_bot):
    """Create a dispatcher instance with memory storage."""
    storage = MemoryStorage()
    return Dispatcher(storage=storage)


@pytest.fixture
def mock_message():
    """Create a mock message for testing."""
    message = MagicMock()
    message.from_user.id = 123456789
    message.from_user.username = "test_user"
    message.chat.id = 123456789
    message.message_id = 1
    
    # Create answer and edit_text methods as AsyncMock
    message.answer = AsyncMock()
    message.edit_text = AsyncMock()
    
    return message


@pytest.fixture
def mock_admin_message():
    """Create a mock message for testing with admin ID."""
    message = MagicMock()
    message.from_user.id = 6629163755  # Admin ID
    message.from_user.username = "admin_user"
    message.chat.id = 6629163755
    message.message_id = 1
    
    # Create answer and edit_text methods as AsyncMock
    message.answer = AsyncMock()
    message.edit_text = AsyncMock()
    
    return message


@pytest.fixture
def mock_callback_query():
    """Create a mock callback query for testing."""
    callback = MagicMock()
    callback.from_user.id = 123456789
    callback.from_user.username = "test_user"
    callback.message.chat.id = 123456789
    callback.message.message_id = 1
    
    # Create answer method as AsyncMock
    callback.answer = AsyncMock()
    callback.message.edit_text = AsyncMock()
    
    return callback


@pytest.fixture
def mock_state():
    """Create a mock FSM context for testing."""
    state = AsyncMock()
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.clear = AsyncMock()
    
    return state 