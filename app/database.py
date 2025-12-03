import aiosqlite
import os
from typing import Optional, Dict
from datetime import datetime


class Database:
    """Database handler for user registration"""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize the database and create tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    email TEXT,
                    registered_at TEXT,
                    UNIQUE(user_id)
                )
            """)
            await db.commit()
    
    async def user_exists(self, user_id: int) -> bool:
        """Check if a user is already registered"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT user_id FROM users WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                result = await cursor.fetchone()
                return result is not None
    
    async def register_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> bool:
        """Register a new user in the database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO users (user_id, username, first_name, last_name, phone, email, registered_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    username,
                    first_name,
                    last_name,
                    phone,
                    email,
                    datetime.now().isoformat()
                ))
                await db.commit()
                return True
        except aiosqlite.IntegrityError:
            # User already exists
            return False
    
    async def update_user(
        self,
        user_id: int,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> bool:
        """Update user information"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                updates = []
                params = []
                
                if phone is not None:
                    updates.append("phone = ?")
                    params.append(phone)
                
                if email is not None:
                    updates.append("email = ?")
                    params.append(email)
                
                if not updates:
                    return False
                
                params.append(user_id)
                query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
                await db.execute(query, params)
                await db.commit()
                return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user information by user_id"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'user_id': row[0],
                        'username': row[1],
                        'first_name': row[2],
                        'last_name': row[3],
                        'phone': row[4],
                        'email': row[5],
                        'registered_at': row[6]
                    }
                return None
    
    async def get_all_users(self) -> list:
        """Get all registered users"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM users") as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        'user_id': row[0],
                        'username': row[1],
                        'first_name': row[2],
                        'last_name': row[3],
                        'phone': row[4],
                        'email': row[5],
                        'registered_at': row[6]
                    }
                    for row in rows
                ]


# Global database instance
db = Database()

