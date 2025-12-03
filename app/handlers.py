from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import re

import app.keyboards as kb
from app.api_client import get_api_client
from app.database import db

router = Router()
api_client = get_api_client()


class BrowseState(StatesGroup):
    """States for browse filtering"""
    browsing = State()


class RegistrationState(StatesGroup):
    """States for user registration"""
    waiting_for_phone = State()
    waiting_for_email = State()


@router.message(CommandStart())
async def start_handler(message: Message):
    """Handle /start command"""
    welcome_text = (
        "👋 Welcome to the Clothing Catalog Bot!\n\n"
        "Use /help to see available commands.\n"
        "Use /browse to explore our clothing collection with filters."
    )
    await message.answer(welcome_text)


@router.message(Command("help"))
async def help_handler(message: Message):
    """Handle /help command - show command list"""
    help_text = (
        "📋 <b>Available Commands:</b>\n\n"
        "/start - Start the bot and see welcome message\n"
        "/help - Show this help message\n"
        "/browse - Browse clothing collection with filters\n"
        "/register - Register your account\n\n"
        "💡 <i>Use /browse to explore items. Filter by category (Men's or Women's clothing) using the buttons.</i>"
    )
    await message.answer(help_text, reply_markup=kb.get_main_keyboard())


@router.message(Command("register"))
async def register_handler(message: Message, state: FSMContext):
    """Handle /register command - start registration process"""
    user_id = message.from_user.id
    
    # Check if user is already registered
    if await db.user_exists(user_id):
        user = await db.get_user(user_id)
        await message.answer(
            f"✅ You are already registered!\n\n"
            f"📝 <b>Your Information:</b>\n"
            f"👤 Name: {user.get('first_name', 'N/A')} {user.get('last_name', '')}\n"
            f"📱 Phone: {user.get('phone', 'Not provided')}\n"
            f"📧 Email: {user.get('email', 'Not provided')}\n"
            f"📅 Registered: {user.get('registered_at', 'N/A')[:10]}"
        )
        return
    
    # Start registration
    await state.set_state(RegistrationState.waiting_for_phone)
    await state.update_data(
        user_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    await message.answer(
        "📝 <b>Registration</b>\n\n"
        "Please provide your phone number.\n"
        "You can send it in any format (e.g., +1234567890, 123-456-7890, etc.)\n\n"
        "Or type /cancel to cancel registration.",
        reply_markup=kb.get_registration_cancel_keyboard()
    )


@router.message(RegistrationState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Process phone number input"""
    phone = message.text.strip()
    
    # Basic phone validation (just check it's not empty and has some digits)
    if not phone or not re.search(r'\d', phone):
        await message.answer(
            "❌ Please provide a valid phone number.\n"
            "You can send it in any format.\n\n"
            "Or type /cancel to cancel registration."
        )
        return
    
    await state.update_data(phone=phone)
    await state.set_state(RegistrationState.waiting_for_email)
    
    await message.answer(
        "📧 <b>Email Address</b>\n\n"
        "Please provide your email address.\n\n"
        "Or type /cancel to cancel registration.",
        reply_markup=kb.get_registration_cancel_keyboard()
    )


@router.message(RegistrationState.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    """Process email input and complete registration"""
    email = message.text.strip()
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        await message.answer(
            "❌ Please provide a valid email address.\n"
            "Format: example@domain.com\n\n"
            "Or type /cancel to cancel registration."
        )
        return
    
    # Get all registration data
    data = await state.get_data()
    
    # Register user in database
    success = await db.register_user(
        user_id=data.get('user_id'),
        username=data.get('username'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone=data.get('phone'),
        email=email
    )
    
    if success:
        await message.answer(
            "✅ <b>Registration Successful!</b>\n\n"
            f"👤 <b>Name:</b> {data.get('first_name', 'N/A')} {data.get('last_name', '')}\n"
            f"📱 <b>Phone:</b> {data.get('phone', 'N/A')}\n"
            f"📧 <b>Email:</b> {email}\n\n"
            "Thank you for registering! You can now use all features of the bot.",
            reply_markup=kb.get_main_keyboard()
        )
    else:
        await message.answer(
            "❌ Registration failed. You may already be registered.\n"
            "Use /help to see available commands."
        )
    
    await state.clear()


@router.message(Command("cancel"))
async def cancel_registration(message: Message, state: FSMContext):
    """Cancel registration process"""
    current_state = await state.get_state()
    if current_state and "RegistrationState" in str(current_state):
        await state.clear()
        await message.answer(
            "❌ Registration cancelled.\n\n"
            "Use /register to start registration again.",
            reply_markup=kb.get_main_keyboard()
        )
    else:
        await message.answer("No active registration to cancel.")


@router.callback_query(F.data == "cancel_registration")
async def cancel_registration_callback(callback: CallbackQuery, state: FSMContext):
    """Handle cancel registration button"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Registration cancelled.\n\n"
        "Use /register to start registration again."
    )
    await callback.answer("Registration cancelled")




@router.message(Command("browse"))
async def browse_handler(message: Message, state: FSMContext):
    """Handle /browse command - show all available items with filters"""
    await state.set_state(BrowseState.browsing)
    await state.update_data(clothing=None)
    
    await message.answer("🔍 Loading items from collection...")
    
    items = await api_client.get_all_items(limit=10)
    
    if items:
        response = api_client.format_items_list(items, max_items=10)
        await message.answer(
            response,
            reply_markup=kb.get_browse_keyboard_with_filters()
        )
    else:
        await message.answer(
            "❌ Could not load items at the moment. Please try again later.",
            reply_markup=kb.get_main_keyboard()
        )


async def _apply_filters_and_show_results(callback: CallbackQuery, state: FSMContext):
    """Helper function to apply filters and show results"""
    data = await state.get_data()
    clothing = data.get("clothing")
    
    await callback.message.edit_text("🔍 Searching...")
    
    # Build active filters text
    if clothing:
        display_name = "Men's Clothing" if clothing == "men's clothing" else "Women's Clothing"
        filter_text = f"🔍 <b>Filter:</b> {display_name}\n\n"
    else:
        filter_text = "📦 <b>All Items:</b>\n\n"
    
    # Search with filters (clothing category)
    items = await api_client.search_items(
        clothing_type=clothing,
        limit=10
    )
    
    # Format response
    response = filter_text
    
    if items:
        response += api_client.format_items_list(items, max_items=10)
    else:
        response += "❌ No items found matching your filters.\nTry adjusting your filters."
    
    await callback.message.edit_text(
        response,
        reply_markup=kb.get_browse_keyboard_with_filters(clothing)
    )
    await callback.answer()


@router.callback_query(F.data == "browse_all", BrowseState.browsing)
async def browse_all_callback(callback: CallbackQuery, state: FSMContext):
    """Handle browse all button - clear filters"""
    await state.update_data(clothing=None)
    await callback.message.edit_text("🔍 Loading all items...")
    
    items = await api_client.get_all_items(limit=10)
    
    if items:
        response = api_client.format_items_list(items, max_items=10)
        await callback.message.edit_text(
            response,
            reply_markup=kb.get_browse_keyboard_with_filters()
        )
    else:
        await callback.message.edit_text(
            "❌ Could not load items at the moment. Please try again later."
        )
    await callback.answer()


@router.callback_query(F.data.startswith("filter_clothing_"), BrowseState.browsing)
async def filter_clothing(callback: CallbackQuery, state: FSMContext):
    """Handle clothing category filter selection"""
    category = callback.data.replace("filter_clothing_", "")
    data = await state.get_data()
    
    # Toggle filter - if same category selected, clear it
    if data.get("clothing") == category:
        await state.update_data(clothing=None)
    else:
        await state.update_data(clothing=category)
    
    await _apply_filters_and_show_results(callback, state)


@router.callback_query(F.data == "show_clothing_filters", BrowseState.browsing)
async def show_clothing_filters(callback: CallbackQuery, state: FSMContext):
    """Show clothing category filter options"""
    data = await state.get_data()
    await callback.message.edit_text(
        "👕 <b>Filter by Category:</b>\n\nSelect a category to filter the collection.",
        reply_markup=kb.get_filter_section_keyboard('clothing', data.get("clothing"))
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_browse", BrowseState.browsing)
async def back_to_browse(callback: CallbackQuery, state: FSMContext):
    """Return to browse view with current filters"""
    await _apply_filters_and_show_results(callback, state)


@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    """Handle back to start button"""
    await state.clear()
    await callback.message.edit_text(
        "🏠 <b>Back to main menu</b>\n\n"
        "Use /browse to explore the collection.",
        reply_markup=None
    )
    await callback.answer()


@router.message()
async def echo_handler(message: Message):
    """Handle any other messages"""
    await message.answer(
        "I don't understand that command. Use /help to see available commands."
    )
