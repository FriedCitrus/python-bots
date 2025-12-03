import os
import aiohttp
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class ClothingAPIClient:
    """Client for fetching clothing collections from FakeStore API"""
    
    def __init__(self):
        # Use FakeStore API
        self.api_url = 'https://fakestoreapi.com'
        self.timeout = aiohttp.ClientTimeout(total=10)
        
        # Allowed categories - only show clothing items
        self.allowed_categories = [
            "men's clothing",
            "women's clothing"
        ]
        
        # Map our clothing types to FakeStore categories
        self.category_mapping = {
            'T-Shirt': "men's clothing",
            'Shirt': "men's clothing",
            'Jeans': "men's clothing",
            'Jacket': "men's clothing",
            'Dress': "women's clothing",
            'Shorts': "men's clothing",
        }
    
    async def _make_request(self, endpoint: str):
        """Make an async HTTP request to the FakeStore API
        Returns: Dict, List, or None depending on the endpoint
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"API request failed with status {response.status}")
                        return None
        except aiohttp.ClientError as e:
            print(f"API request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def _transform_product(self, product: Dict) -> Dict:
        """Transform FakeStore product to our format"""
        return {
            'id': str(product.get('id', '')),
            'name': product.get('title', 'Unknown'),
            'title': product.get('title', 'Unknown'),
            'price': product.get('price', 0),
            'cost': product.get('price', 0),
            'description': product.get('description', ''),
            'details': product.get('description', ''),
            'category': product.get('category', ''),
            'image': product.get('image', ''),
            'rating': product.get('rating', {}),
            # FakeStore doesn't have size/material, so we'll use defaults
            'size': 'N/A',
            'material': 'N/A',
            'type': self._get_clothing_type_from_category(product.get('category', ''))
        }
    
    def _is_allowed_category(self, category: str) -> bool:
        """Check if a category is in the allowed list"""
        if not category:
            return False
        category_lower = category.lower()
        return any(allowed.lower() == category_lower for allowed in self.allowed_categories)
    
    def _get_clothing_type_from_category(self, category: str) -> str:
        """Map FakeStore category back to our clothing type"""
        category_lower = category.lower()
        if "men's clothing" in category_lower or "women's clothing" in category_lower:
            # Try to infer from title or return generic
            return "Clothing"
        return category
    
    def _filter_clothing_items(self, products: List[Dict]) -> List[Dict]:
        """Filter products to only include clothing categories"""
        if not products:
            return []
        
        filtered = []
        for product in products:
            category = product.get('category', '')
            if self._is_allowed_category(category):
                filtered.append(product)
        
        return filtered
    
    async def get_all_items(self, limit: int = 20) -> List[Dict]:
        """Fetch all products from FakeStore API, filtered to only clothing items"""
        data = await self._make_request('products')
        
        if data and isinstance(data, list):
            # Filter to only clothing categories
            clothing_items = self._filter_clothing_items(data)
            
            # Transform and limit
            transformed = [self._transform_product(item) for item in clothing_items[:limit]]
            return transformed
        
        return []
    
    async def search_items(
        self, 
        clothing_type: Optional[str] = None,
        size: Optional[str] = None,
        material: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Search for clothing items with filters"""
        # clothing_type now directly contains the category (e.g., "men's clothing" or "women's clothing")
        # FakeStore API doesn't support size/material filters, so we ignore those
        if clothing_type and self._is_allowed_category(clothing_type):
            # Get products by category
            data = await self._make_request(f"products/category/{clothing_type}")
        else:
            # Get all products
            data = await self._make_request('products')
        
        if not data:
            return []
        
        if not isinstance(data, list):
            data = [data]
        
        # Filter to only clothing categories (skip electronics, jewelry, etc.)
        clothing_items = self._filter_clothing_items(data)
        
        # Transform products
        transformed = [self._transform_product(item) for item in clothing_items]
        
        # Limit results
        return transformed[:limit]
    
    async def get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """Get a specific product by ID from FakeStore API, only if it's clothing"""
        data = await self._make_request(f'products/{item_id}')
        if data:
            # Check if it's a clothing item before returning
            category = data.get('category', '')
            if self._is_allowed_category(category):
                return self._transform_product(data)
        return None
    
    async def get_categories(self) -> List[str]:
        """Get all available categories from FakeStore API"""
        data = await self._make_request('products/categories')
        if data and isinstance(data, list):
            return data
        return []
    
    def format_item_message(self, item: Dict) -> str:
        """Format a product item as a message"""
        name = item.get('name', item.get('title', 'Unknown Item'))
        price = item.get('price', item.get('cost', 'N/A'))
        category = item.get('category', 'N/A')
        description = item.get('description', item.get('details', ''))
        rating = item.get('rating', {})
        
        message = f"🛍️ <b>{name}</b>\n\n"
        
        if price != 'N/A':
            message += f"💰 <b>Price:</b> ${price:.2f}\n"
        
        if category != 'N/A':
            message += f"📂 <b>Category:</b> {category}\n"
        
        if rating and isinstance(rating, dict):
            rate = rating.get('rate', 'N/A')
            count = rating.get('count', 0)
            if rate != 'N/A':
                message += f"⭐ <b>Rating:</b> {rate}/5 ({count} reviews)\n"
        
        if description:
            # Truncate description if too long
            desc = description[:200] + "..." if len(description) > 200 else description
            message += f"\n📝 {desc}"
        
        return message
    
    def format_items_list(self, items: List[Dict], max_items: int = 5) -> str:
        """Format a list of items as a message"""
        if not items:
            return "❌ No items found."
        
        message = f"📦 <b>Found {len(items)} items:</b>\n\n"
        
        for i, item in enumerate(items[:max_items], 1):
            name = item.get('name', item.get('title', 'Unknown'))
            price = item.get('price', item.get('cost', 'N/A'))
            category = item.get('category', '')
            rating = item.get('rating', {})
            
            message += f"{i}. <b>{name}</b>"
            if price != 'N/A':
                message += f" - ${price:.2f}"
            if category:
                message += f" ({category})"
            if rating and isinstance(rating, dict) and rating.get('rate'):
                message += f" ⭐{rating.get('rate', '')}"
            message += "\n"
        
        if len(items) > max_items:
            message += f"\n... and {len(items) - max_items} more items"
        
        return message


# Mock data generator for testing when API is not configured
class MockAPIClient:
    """Mock API client that returns sample data for testing"""
    
    MOCK_ITEMS = [
        {
            'id': '1',
            'name': 'Classic Cotton T-Shirt',
            'type': 'T-Shirt',
            'size': 'M',
            'material': 'Cotton',
            'price': 29.99,
            'description': 'Comfortable classic fit t-shirt made from 100% organic cotton.'
        },
        {
            'id': '2',
            'name': 'Slim Fit Denim Jeans',
            'type': 'Jeans',
            'size': 'L',
            'material': 'Denim',
            'price': 79.99,
            'description': 'Modern slim fit jeans with stretch for comfort.'
        },
        {
            'id': '3',
            'name': 'Wool Winter Jacket',
            'type': 'Jacket',
            'size': 'XL',
            'material': 'Wool',
            'price': 149.99,
            'description': 'Warm winter jacket perfect for cold weather.'
        },
        {
            'id': '4',
            'name': 'Silk Summer Dress',
            'type': 'Dress',
            'size': 'S',
            'material': 'Silk',
            'price': 89.99,
            'description': 'Elegant summer dress with flowing silk fabric.'
        },
        {
            'id': '5',
            'name': 'Linen Casual Shirt',
            'type': 'Shirt',
            'size': 'M',
            'material': 'Linen',
            'price': 49.99,
            'description': 'Breathable linen shirt for warm weather.'
        },
    ]
    
    async def search_items(
        self,
        clothing_type: Optional[str] = None,
        size: Optional[str] = None,
        material: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Search mock items with filters"""
        results = self.MOCK_ITEMS.copy()
        
        if clothing_type:
            results = [item for item in results if item.get('type', '').lower() == clothing_type.lower()]
        
        if size:
            results = [item for item in results if item.get('size', '') == size]
        
        if material:
            results = [item for item in results if item.get('material', '').lower() == material.lower()]
        
        return results[:limit]
    
    async def get_all_items(self, limit: int = 20) -> List[Dict]:
        """Get all mock items"""
        return self.MOCK_ITEMS[:limit]
    
    def format_item_message(self, item: Dict) -> str:
        """Format item message (same as real client)"""
        client = ClothingAPIClient()
        return client.format_item_message(item)
    
    def format_items_list(self, items: List[Dict], max_items: int = 5) -> str:
        """Format items list (same as real client)"""
        client = ClothingAPIClient()
        return client.format_items_list(items, max_items)


def get_api_client():
    """Get the API client - always use FakeStore API now"""
    return ClothingAPIClient()

