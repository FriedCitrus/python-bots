# Telegram Clothing Catalog Bot

A simple Telegram bot built with aiogram that allows users to browse a clothing catalog and make queries by selecting clothing pieces, sizes, and materials.

## Features

- `/start` - Welcome message
- `/help` - Show available commands
- `/catalog` - Interactive catalog query system with:
  - Clothing piece selection (T-Shirt, Shirt, Jeans, Jacket, Dress, Shorts)
  - Size selection (S, M, L, XL, XXL)
  - Material selection (Cotton, Polyester, Denim, Wool, Silk, Linen)
  - **NEW**: Fetches real items from API based on your selections
- `/browse` - Browse all available items from the clothing collection API

## Setup

### 1. Get a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token you receive

### 2. Install Dependencies

```bash
# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

1. Create a `.env` file in the project root:
   ```bash
   touch .env
   ```

2. Edit `.env` and add your bot token (required):
   ```
   BOT_TOKEN=your_actual_bot_token_here
   ```
   
   **Note**: The bot uses the FakeStore API (https://fakestoreapi.com) which requires no API key or configuration.

### 4. Run the Bot

```bash
python main.py
```

The bot will start polling for messages. You should see "Bot is starting..." in the console.

## Project Structure

```
pyt/
├── app/
│   ├── __init__.py      # Package initialization
│   ├── handlers.py      # Bot command handlers
│   ├── keyboards.py     # Inline keyboard definitions
│   └── api_client.py    # API client for clothing collections
├── main.py              # Bot entry point
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
└── README.md            # This file
```

## Usage

1. Start a chat with your bot on Telegram
2. Send `/start` to begin
3. **Browse items**: Send `/browse` to see all available items from the collection
4. **Filter items**: Use the filter buttons in `/browse` to:
   - Filter by clothing type (T-Shirt, Shirt, Jeans, Jacket, Dress, Shorts)
   - Filter by size (S, M, L, XL, XXL) - Note: FakeStore doesn't provide size data
   - Filter by material (Cotton, Polyester, etc.) - Note: FakeStore doesn't provide material data
   - Combine multiple filters to narrow down results

## API Integration

The bot uses the **FakeStore API** (https://fakestoreapi.com) to fetch product data. This is a free, public API that provides fake e-commerce product data for testing and development.

### FakeStore API Endpoints Used

- `GET /products` - Get all products
- `GET /products/{id}` - Get a specific product by ID
- `GET /products/category/{category}` - Get products by category

### Product Data Structure

FakeStore API returns products with the following structure:
```json
{
  "id": 1,
  "title": "Fjallraven - Foldsack No. 1 Backpack",
  "price": 109.95,
  "description": "Your perfect pack for everyday use...",
  "category": "men's clothing",
  "image": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
  "rating": {
    "rate": 3.9,
    "count": 120
  }
}
```

### Category Mapping

The bot maps clothing types to FakeStore categories:
- T-Shirt, Shirt, Jeans, Jacket, Shorts → `men's clothing`
- Dress → `women's clothing`

**Note**: FakeStore API doesn't provide size or material information, so these filters will show all items from the selected category. The bot displays category and rating information instead.

## Deployment

To deploy this bot, you can:

1. **Run on a VPS/Server**: Follow the setup steps above on your server
2. **Use systemd service** (Linux): Create a service file to keep the bot running
3. **Use Docker**: Create a Dockerfile and run in a container
4. **Use cloud platforms**: Deploy to platforms like Heroku, Railway, or Render

### Example systemd service (Linux)

Create `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/pyt
Environment="PATH=/path/to/pyt/.venv/bin"
ExecStart=/path/to/pyt/.venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

## Notes

- Make sure to keep your `.env` file secure and never commit it to version control
- The bot uses aiogram 3.x with FSM (Finite State Machine) for handling multi-step interactions
- All keyboards are inline keyboards for better user experience
- The API client uses async HTTP requests (aiohttp) for better performance
- If your API uses a different format, you can modify `app/api_client.py` to match your API structure

