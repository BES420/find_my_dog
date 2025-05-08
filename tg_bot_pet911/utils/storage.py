import json
import os
import uuid
import aiofiles
from datetime import datetime
from aiogram import Bot
from typing import Dict, Any, List, Tuple

from tg_bot_pet911.app.models import PetInfo, PetPhoto


# Base path for storing data
BASE_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PETS_DATA_PATH = os.path.join(BASE_DATA_PATH, "pets")


async def save_pet_data(pet_info: PetInfo, bot: Bot) -> Tuple[str, Dict[str, Any]]:
    """
    Save pet data to a JSON file and download photos.
    
    Args:
        pet_info: PetInfo object containing pet data
        bot: Bot instance for downloading photos
    
    Returns:
        Tuple containing (path to the saved data directory, pet data as dict)
    """
    # Create a unique ID for this pet
    pet_id = str(uuid.uuid4())[:8]  # Use shorter UUID for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create a clean type and gender string for the folder name
    pet_type_str = pet_info.pet_type if pet_info.pet_type else "unknown"
    gender_str = pet_info.gender if pet_info.gender else "unknown"
    
    # Create more descriptive directory name
    pet_dir_name = f"{timestamp}_{pet_type_str}_{gender_str}_{pet_id}"
    
    # Create directory for this pet
    pet_dir = os.path.join(PETS_DATA_PATH, pet_dir_name)
    os.makedirs(pet_dir, exist_ok=True)
    
    # Download photos directly to the data directory
    photo_paths = []
    if pet_info.photos:
        for i, photo in enumerate(pet_info.photos):
            # Get file info
            file_info = await bot.get_file(photo.file_id)
            file_path = file_info.file_path
            
            # Create local path for the photo with better naming
            ext = os.path.splitext(file_path)[1] or ".jpg"  # Default to .jpg if no extension
            local_filename = f"{pet_type_str}_{gender_str}_{pet_id}_image_{i+1}{ext}"
            local_path = os.path.join(pet_dir, local_filename)
            
            # Download the file
            await bot.download_file(file_path, local_path)
            photo_paths.append(local_filename)
    
    # Prepare data for JSON
    pet_data = pet_info.model_dump()
    
    # Add extra info
    pet_data["id"] = pet_id
    
    # Format datetime in a more human-readable way
    current_time = datetime.now()
    pet_data["created_at"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
    pet_data["photo_files"] = photo_paths
    
    # Add human-readable pet type and gender
    pet_type_map = {
        "dog": "Собака", 
        "cat": "Кошка", 
        "other": "Другое животное"
    }
    
    gender_map = {
        "male": "Мальчик",
        "female": "Девочка",
        "unknown": "Пол неизвестен"
    }
    
    pet_data["pet_type_text"] = pet_type_map.get(pet_data["pet_type"], "Неизвестно")
    pet_data["gender_text"] = gender_map.get(pet_data["gender"], "Неизвестно")
    
    # Remove bulky file_ids from the JSON to keep it clean
    if "photos" in pet_data:
        del pet_data["photos"]
    
    # Save JSON data with matching name to photos
    json_path = os.path.join(pet_dir, f"{pet_type_str}_{gender_str}_{pet_id}_data.json")
    async with aiofiles.open(json_path, "w", encoding="utf-8") as f:
        json_str = json.dumps(pet_data, ensure_ascii=False, indent=2)
        await f.write(json_str)
    
    return pet_dir, pet_data 