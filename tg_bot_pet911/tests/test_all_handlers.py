import pytest
import asyncio
import importlib
import inspect
import traceback
from typing import List, Dict, Any, Tuple
from unittest.mock import MagicMock, AsyncMock, patch
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

# Импортируем модуль тестов, а не конкретные тесты
# Это позволит избежать проблем с импортами
from tg_bot_pet911.tests import (
    test_start_handler,
    test_gender_handler,
    test_photo_handler,
    test_location_handler,
    test_comment_handler,
    test_confirm_handler,
    test_cancel_handler
)


async def run_all_tests(admin_chat_id: int = None) -> List[Dict[str, Any]]:
    """
    Run all test functions and return results.
    
    Args:
        admin_chat_id: Chat ID to send results to (for bot)
        
    Returns:
        List of test results
    """
    test_modules = [
        test_start_handler,
        test_gender_handler,
        test_photo_handler,
        test_location_handler,
        test_comment_handler,
        test_confirm_handler,
        test_cancel_handler
    ]
    
    results = []
    
    for module in test_modules:
        module_name = module.__name__.split('.')[-1]
        
        # Get all test functions in the module
        test_funcs = [
            func for name, func in inspect.getmembers(module, inspect.isfunction)
            if name.startswith('test_')
        ]
        
        for test_func in test_funcs:
            test_name = test_func.__name__
            full_test_name = f"{module_name}.{test_name}"
            
            # Create fixtures manually
            mock_message = MagicMock()
            mock_message.from_user.id = 123456789
            mock_message.from_user.username = "test_user"
            mock_message.chat.id = 123456789
            mock_message.message_id = 1
            mock_message.answer = AsyncMock()
            mock_message.edit_text = AsyncMock()
            
            mock_callback_query = MagicMock()
            mock_callback_query.from_user.id = 123456789
            mock_callback_query.from_user.username = "test_user"
            mock_callback_query.message.chat.id = 123456789
            mock_callback_query.message.message_id = 1
            mock_callback_query.answer = AsyncMock()
            mock_callback_query.message.edit_text = AsyncMock()
            
            mock_state = AsyncMock()
            mock_state.set_state = AsyncMock()
            mock_state.update_data = AsyncMock()
            mock_state.get_data = AsyncMock(return_value={})
            mock_state.clear = AsyncMock()
            
            mock_bot = MagicMock()
            
            try:
                # Get the signature to check what parameters the test function needs
                sig = inspect.signature(test_func)
                params = {}
                
                # Map fixtures to parameters
                fixtures_map = {
                    'mock_message': mock_message,
                    'mock_callback_query': mock_callback_query,
                    'mock_state': mock_state,
                    'mock_bot': mock_bot,
                }
                
                for param_name in sig.parameters:
                    if param_name in fixtures_map:
                        params[param_name] = fixtures_map[param_name]
                
                # Run the test
                await test_func(**params)
                
                results.append({
                    'test': full_test_name,
                    'status': 'PASS',
                    'error': None
                })
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                results.append({
                    'test': full_test_name,
                    'status': 'FAIL',
                    'error': error_msg
                })
                
    return results


def format_test_results(results: List[Dict[str, Any]]) -> str:
    """Format test results into a readable string."""
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = total - passed
    
    output = [
        f"🧪 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ 🧪",
        f"✅ Успешно: {passed}/{total}",
        f"❌ Провалено: {failed}/{total}",
        "\n📋 Детали:"
    ]
    
    for result in results:
        status_emoji = "✅" if result['status'] == 'PASS' else "❌"
        output.append(f"{status_emoji} {result['test']}")
        
        if result['error']:
            # Limit error message length
            error_msg = result['error'][:200] + "..." if len(result['error']) > 200 else result['error']
            output.append(f"   ⚠️ {error_msg}")
    
    return "\n".join(output)


# Create router for the bot command
router = Router()


@router.message(Command("test"))
async def cmd_test(message: Message, state: FSMContext):
    """Run all tests and send results to the chat."""
    user_id = message.from_user.id
    
    # Check if user is admin
    if user_id != 6629163755:  # Your admin ID
        await message.answer("⛔ Только администратор может запустить тесты.")
        return
    
    # Send initial message
    await message.answer("🧪 Запуск тестов... Это может занять некоторое время.")
    
    # Run tests
    results = await run_all_tests()
    
    # Format and send results
    formatted_results = format_test_results(results)
    await message.answer(formatted_results)


# For running the tests outside of the bot
@pytest.mark.asyncio
async def test_all_handlers():
    """Run all handler tests."""
    results = await run_all_tests()
    
    # Assert that all tests passed
    failed_tests = [r for r in results if r['status'] == 'FAIL']
    if failed_tests:
        for test in failed_tests:
            print(f"❌ {test['test']} failed: {test['error']}")
        pytest.fail(f"{len(failed_tests)} tests failed")
    
    # Print success message
    print(f"✅ All {len(results)} tests passed!") 