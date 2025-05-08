from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class PetLocation(BaseModel):
    """Pet location data model."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Check if location is valid."""
        return (self.latitude is not None and self.longitude is not None) or self.address is not None


class PetPhoto(BaseModel):
    """Pet photo data model."""
    file_id: str
    file_unique_id: str


class PetInfo(BaseModel):
    """Pet information data model."""
    user_id: int
    chat_id: int
    username: Optional[str] = None
    
    # Step 1: Pet type
    pet_type: str
    
    # Step 2: Gender
    gender: str
    
    # Step 3: Photos
    photos: List[PetPhoto] = Field(default_factory=list)
    
    # Step 4: Location
    location: PetLocation = Field(default_factory=PetLocation)
    
    # Step 5: Comments
    comment: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    
    def is_complete(self) -> bool:
        """Check if all required information is filled."""
        return (
            self.pet_type and 
            self.gender and 
            len(self.photos) > 0 and 
            self.location.is_valid()
        )
    
    def format_for_publication(self) -> str:
        """Format pet information for publication."""
        pet_type_map = {
            "dog": "🐶 Собака", 
            "cat": "🐱 Кошка", 
            "other": "🐾 Другое животное"
        }
        
        gender_map = {
            "male": "♂️ Мальчик",
            "female": "♀️ Девочка",
            "unknown": "❓ Пол неизвестен"
        }
        
        parts = [
            f"🆘 НАЙДЕН ПИТОМЕЦ 🆘\n",
            f"Вид: {pet_type_map.get(self.pet_type, 'Неизвестно')}",
            f"Пол: {gender_map.get(self.gender, 'Неизвестно')}"
        ]
        
        # Add location
        if self.location.address:
            parts.append(f"📍 Локация: {self.location.address}")
        elif self.location.latitude and self.location.longitude:
            parts.append(f"📍 Координаты: {self.location.latitude}, {self.location.longitude}")
        
        # Add comment if exists
        if self.comment:
            parts.append(f"\n💬 Дополнительная информация:\n{self.comment}")
        
        # Add contact info (username if available, otherwise user ID)
        if self.username:
            parts.append(f"\n📱 Связаться: @{self.username}")
        else:
            parts.append(f"\n📱 ID для связи: {self.user_id}")
        
        return "\n".join(parts) 