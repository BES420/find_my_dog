from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError
import json

from tg_bot_pet911.app.models import PetInfo, PetPhoto
from tg_bot_pet911.config.config import CHANNEL_ID, ADMIN_IDS, NOTIFICATION_ID
from tg_bot_pet911.states.pet_states import PetRegistration
from tg_bot_pet911.utils.storage import save_pet_data


router = Router()


async def send_notification(bot: Bot, pet_info: PetInfo, saved_dir: str, pet_data_json: str):
    """Send notification to the main notification ID about new pet entry."""
    try:
        # Get photos for notification
        photos = pet_info.photos
        
        # Format notification message
        notification_text = (
            f"🆕 НОВОЕ ОБЪЯВЛЕНИЕ О ПИТОМЦЕ!\n\n"
            f"🐾 Тип: {pet_info.pet_type_text if hasattr(pet_info, 'pet_type_text') else pet_info.pet_type}\n"
            f"🧬 Пол: {pet_info.gender_text if hasattr(pet_info, 'gender_text') else pet_info.gender}\n"
            f"🗺️ Локация: {'GPS координаты' if pet_info.location.latitude else pet_info.location.address or 'Не указана'}\n"
            f"👤 Пользователь: {pet_info.username or pet_info.user_id}\n\n"
            f"📂 Сохранено в: {saved_dir}\n\n"
            f"💾 Данные:\n<pre>{pet_data_json[:500]}...</pre>" # Limit JSON to 500 chars to avoid message too long
        )
        
        # Send text notification first
        await bot.send_message(
            chat_id=NOTIFICATION_ID,
            text=notification_text,
            parse_mode="HTML"
        )
        
        # Send photos as separate messages to avoid large media groups
        if photos:
            for i, photo in enumerate(photos[:3]):  # Limit to 3 photos max
                await bot.send_photo(
                    chat_id=NOTIFICATION_ID,
                    photo=photo.file_id,
                    caption=f"Фото {i+1} из объявления"
                )
                
    except TelegramAPIError as e:
        print(f"Failed to send notification: {e}")


@router.callback_query(PetRegistration.confirming, F.data == "confirm:yes")
async def confirm_submission(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Handle confirmation and publish the announcement."""
    # Get current state data
    data = await state.get_data()
    pet_info_dict = data.get("pet_info", {})
    
    # Create PetInfo object
    pet_info = PetInfo(**pet_info_dict)
    
    # Save the data locally
    pet_data_json = None
    try:
        saved_dir, pet_data = await save_pet_data(pet_info, bot)
        local_save_success = True
        
        # Convert to pretty JSON string for output
        pet_data_json = json.dumps(pet_data, ensure_ascii=False, indent=2)
        
        # Send notification to the main notification ID
        await send_notification(bot, pet_info, saved_dir, pet_data_json)
        
    except Exception as e:
        local_save_success = False
        saved_dir = None
        print(f"Error saving pet data: {e}")
    
    # Check if we have a channel to publish to
    if CHANNEL_ID:
        try:
            # Get photo IDs
            photos = [PetPhoto(**photo) for photo in pet_info_dict.get("photos", [])]
            
            if photos:
                # If we have multiple photos, create a media group
                if len(photos) > 1:
                    media = [
                        InputMediaPhoto(
                            media=photos[0].file_id,
                            caption=pet_info.format_for_publication()
                        )
                    ]
                    
                    # Add remaining photos without captions
                    for photo in photos[1:]:
                        media.append(
                            InputMediaPhoto(media=photo.file_id)
                        )
                    
                    # Send as media group
                    await bot.send_media_group(
                        chat_id=CHANNEL_ID,
                        media=media
                    )
                else:
                    # Send as single photo with caption
                    await bot.send_photo(
                        chat_id=CHANNEL_ID,
                        photo=photos[0].file_id,
                        caption=pet_info.format_for_publication()
                    )
                
                # Notify user about successful publication
                success_message = (
                    "✅ Ваше объявление успешно опубликовано в канале!\n\n"
                    "Спасибо за помощь животным! ❤️\n\n"
                )
                
                # Add local save status
                if local_save_success:
                    success_message += f"📁 Данные сохранены локально в: {saved_dir}\n\n"
                    
                    # Add JSON data
                    if pet_data_json:
                        success_message += f"📋 Собранные данные:\n<pre>{pet_data_json}</pre>\n\n"
                
                success_message += "Чтобы создать новое объявление, используйте команду /start."
                
                await callback.message.edit_text(success_message, parse_mode="HTML")
            else:
                # If something went wrong with photos
                await callback.message.edit_text(
                    "⚠️ Произошла ошибка: не найдены фотографии для публикации.\n\n"
                    "Пожалуйста, попробуйте создать объявление заново с помощью команды /start."
                )
        
        except TelegramAPIError as e:
            # Handle API errors
            await callback.message.edit_text(
                f"⚠️ Ошибка при публикации объявления: {str(e)}\n\n"
                f"Пожалуйста, попробуйте позже или обратитесь к администратору."
            )
    else:
        # If no channel ID is configured, send to admin or just confirm to user
        if ADMIN_IDS:
            # Send notification to admins
            admin_message = (
                "🆕 Новое объявление о найденном питомце!\n\n" +
                pet_info.format_for_publication()
            )
            
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(
                        chat_id=admin_id,
                        text=admin_message
                    )
                    
                    # Send photos to admin
                    photos = [PetPhoto(**photo) for photo in pet_info_dict.get("photos", [])]
                    if photos:
                        for photo in photos:
                            await bot.send_photo(
                                chat_id=admin_id,
                                photo=photo.file_id
                            )
                except TelegramAPIError:
                    # Silently ignore if cannot send to an admin
                    pass
        
        # Notify user
        success_message = (
            "✅ Ваше объявление успешно отправлено!"
        )
        
        if ADMIN_IDS:
            success_message += "\n\nПосле проверки администратором оно будет опубликовано."
        
        success_message += "\nСпасибо за помощь животным! ❤️\n\n"
        
        # Add local save status
        if local_save_success:
            success_message += f"📁 Данные сохранены локально в: {saved_dir}\n\n"
            
            # Add JSON data
            if pet_data_json:
                success_message += f"📋 Собранные данные:\n<pre>{pet_data_json}</pre>\n\n"
        
        success_message += "Чтобы создать новое объявление, используйте команду /start."
        
        await callback.message.edit_text(success_message, parse_mode="HTML")
    
    # Clear state
    await state.clear()
    await callback.answer()


@router.callback_query(PetRegistration.confirming, F.data == "confirm:no")
async def reject_submission(callback: CallbackQuery, state: FSMContext):
    """Handle rejection and return to edit."""
    await callback.message.edit_text(
        "🔄 Вы отменили отправку объявления.\n\n"
        "Чтобы начать заново, используйте команду /start."
    )
    await state.clear()
    await callback.answer()


@router.callback_query(PetRegistration.confirming, F.data == "confirm:restart")
async def restart_submission(callback: CallbackQuery, state: FSMContext):
    """Handle restart request."""
    from tg_bot_pet911.keyboards.inline import get_pet_type_keyboard
    
    # Clear current state
    await state.clear()
    
    # Start over
    await callback.message.edit_text(
        "🔄 Начинаем заново.\n\n"
        "Какое животное вы нашли?",
        reply_markup=get_pet_type_keyboard()
    )
    
    # Set state to selecting pet type
    await state.set_state(PetRegistration.selecting_type)
    await callback.answer() 