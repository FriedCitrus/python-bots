from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)


def get_main_keyboard():
    """Main menu keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='/browse'), KeyboardButton(text='/register')],
            [KeyboardButton(text='/help')],
        ],
        resize_keyboard=True,
    )


def get_registration_cancel_keyboard():
    """Keyboard with cancel button for registration"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='❌ Cancel', callback_data='cancel_registration')],
        ],
    )


def get_clothing_keyboard():
    """Keyboard for selecting clothing piece"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='👕 T-Shirt', callback_data='clothing_T-Shirt')],
            [InlineKeyboardButton(text='👔 Shirt', callback_data='clothing_Shirt')],
            [InlineKeyboardButton(text='👖 Jeans', callback_data='clothing_Jeans')],
            [InlineKeyboardButton(text='🧥 Jacket', callback_data='clothing_Jacket')],
            [InlineKeyboardButton(text='👗 Dress', callback_data='clothing_Dress')],
            [InlineKeyboardButton(text='🩳 Shorts', callback_data='clothing_Shorts')],
        ],
    )


def get_clothing_filter_keyboard(active_clothing=None):
    """Keyboard for filtering by clothing category in browse mode"""
    buttons = []
    clothing_categories = [
        ("👔 Men's Clothing", "men's clothing"),
        ("👗 Women's Clothing", "women's clothing"),
    ]
    
    for emoji_text, category in clothing_categories:
        text = emoji_text
        if active_clothing == category:
            text = f"✅ {emoji_text}"
        buttons.append([InlineKeyboardButton(
            text=text,
            callback_data=f'filter_clothing_{category}'
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_size_keyboard():
    """Keyboard for selecting size"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='S', callback_data='size_S'),
                InlineKeyboardButton(text='M', callback_data='size_M'),
                InlineKeyboardButton(text='L', callback_data='size_L'),
            ],
            [
                InlineKeyboardButton(text='XL', callback_data='size_XL'),
                InlineKeyboardButton(text='XXL', callback_data='size_XXL'),
            ],
        ],
    )


def get_size_filter_keyboard(active_size=None):
    """Keyboard for filtering by size in browse mode"""
    sizes = ['S', 'M', 'L', 'XL', 'XXL']
    buttons = []
    row = []
    
    for size in sizes:
        text = size
        if active_size == size:
            text = f"✅ {size}"
        row.append(InlineKeyboardButton(
            text=text,
            callback_data=f'filter_size_{size}'
        ))
        if len(row) == 3:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_material_keyboard():
    """Keyboard for selecting material"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🧵 Cotton', callback_data='material_Cotton')],
            [InlineKeyboardButton(text='🧵 Polyester', callback_data='material_Polyester')],
            [InlineKeyboardButton(text='🧵 Denim', callback_data='material_Denim')],
            [InlineKeyboardButton(text='🧵 Wool', callback_data='material_Wool')],
            [InlineKeyboardButton(text='🧵 Silk', callback_data='material_Silk')],
            [InlineKeyboardButton(text='🧵 Linen', callback_data='material_Linen')],
        ],
    )


def get_material_filter_keyboard(active_material=None):
    """Keyboard for filtering by material in browse mode"""
    materials = [
        ('🧵 Cotton', 'Cotton'),
        ('🧵 Polyester', 'Polyester'),
        ('🧵 Denim', 'Denim'),
        ('🧵 Wool', 'Wool'),
        ('🧵 Silk', 'Silk'),
        ('🧵 Linen', 'Linen'),
    ]
    
    buttons = []
    for emoji_text, material in materials:
        text = emoji_text
        if active_material == material:
            text = f"✅ {emoji_text}"
        buttons.append([InlineKeyboardButton(
            text=text,
            callback_data=f'filter_material_{material}'
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard():
    """Keyboard with back button"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🏠 Back to Start', callback_data='back_to_start')],
        ],
    )


def get_browse_keyboard():
    """Keyboard for browse functionality (deprecated - use get_browse_keyboard_with_filters)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🔄 Refresh', callback_data='browse_all')],
            [InlineKeyboardButton(text='🏠 Back to Start', callback_data='back_to_start')],
        ],
    )


def get_browse_keyboard_with_filters(active_clothing=None):
    """Keyboard for browse functionality with filter buttons"""
    inline_keyboard = [
        [InlineKeyboardButton(text='👕 Filter by Category', callback_data='show_clothing_filters')],
        [
            InlineKeyboardButton(text='🔄 Show All', callback_data='browse_all'),
            InlineKeyboardButton(text='🏠 Back', callback_data='back_to_start'),
        ],
    ]
    
    # Show active filters summary
    if active_clothing:
        display_name = "Men's Clothing" if active_clothing == "men's clothing" else "Women's Clothing"
        inline_keyboard.insert(0, [
            InlineKeyboardButton(
                text=f"✅ Filter: {display_name}",
                callback_data='show_filters_info'
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_filter_section_keyboard(filter_type, active_clothing=None):
    """Get keyboard for a specific filter section"""
    if filter_type == 'clothing':
        keyboard = get_clothing_filter_keyboard(active_clothing)
        # Add back button
        buttons = keyboard.inline_keyboard.copy()
        buttons.append([InlineKeyboardButton(text='🔙 Back to Browse', callback_data='back_to_browse')])
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    return None
