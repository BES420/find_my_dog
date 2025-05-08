import os
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Admin IDs (for notifications)
ADMIN_IDS: List[int] = [
    int(admin_id.strip()) 
    for admin_id in os.getenv("ADMIN_IDS", "").split(",") 
    if admin_id.strip()
]

# Channel ID where pet announcements will be published
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Main notification ID - will always receive notifications for new pet entries
NOTIFICATION_ID = 6629163755

# Redis connection for FSM
REDIS_DSN = os.getenv("REDIS_DSN", "redis://localhost:6379/0")

# Other settings
MAX_PHOTOS = 5  # Maximum number of photos for a pet 