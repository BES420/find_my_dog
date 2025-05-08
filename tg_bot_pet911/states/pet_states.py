from aiogram.fsm.state import State, StatesGroup


class PetRegistration(StatesGroup):
    """Pet registration states."""
    # Step 1: Select pet type (dog, cat, other)
    selecting_type = State()
    
    # Step 2: Select gender
    selecting_gender = State()
    
    # Step 3: Upload photos
    uploading_photos = State()
    
    # Step 4: Location info
    entering_location = State()
    
    # Step 5: Additional comments
    entering_comment = State()
    
    # Step 6: Final confirmation
    confirming = State() 