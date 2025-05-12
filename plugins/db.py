from typing import Any
from config import DB_URI, DB_NAME
from motor import motor_asyncio

client: motor_asyncio.AsyncIOMotorClient[Any] = motor_asyncio.AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]

class Techifybots:
    def __init__(self):
        self.users = db["users"]
        self.meta = db["meta"]
        self.cache: dict[int, dict[str, Any]] = {}

    async def add_user(self, user_id: int, name: str) -> dict[str, Any] | None:
        try:
            user: dict[str, Any] = {"user_id": user_id, "name": name, "session": None}
            await self.users.insert_one(user)
            self.cache[user_id] = user      
            return user
        except Exception as e:
            print("Error in add_user:", e)

    async def get_user(self, user_id: int) -> dict[str, Any] | None:
        try:
            if user_id in self.cache:
                return self.cache[user_id]
            user = await self.users.find_one({"user_id": user_id})
            if user:
                self.cache[user_id] = user
            return user
        except Exception as e:
            print("Error in get_user:", e)
            return None

    async def set_session(self, user_id: int, session: Any) -> bool:
        try:
            result = await self.users.update_one(
                {"user_id": user_id},
                {"$set": {"session": session}}
            )
            if user_id in self.cache:
                self.cache[user_id]["session"] = session
            return result.modified_count > 0
        except Exception as e:
            print("Error in set_session:", e)
            return False

    async def get_session(self, user_id: int) -> Any | None:
        try:
            user = await self.get_user(user_id)
            return user.get("session") if user else None
        except Exception as e:
            print("Error in get_session:", e)
            return None

    async def get_all_users(self) -> list[dict[str, Any]]:
        try:
            users: list[dict[str, Any]] = []
            async for user in self.users.find():
                users.append(user)
            return users
        except Exception as e:
            print("Error in get_all_users:", e)
            return []

    async def delete_user(self, user_id: int) -> bool:
        try:
            result = await self.users.delete_one({"user_id": user_id})
            self.cache.pop(user_id, None)
            return result.deleted_count > 0
        except Exception as e:
            print("Error in delete_user:", e)
            return False

    # Admins
    async def add_admin(self, user_id: int) -> bool:
        try:
            doc = await self.meta.find_one({"_id": "admins"})
            admins = doc.get("list", []) if doc else []
            if user_id in admins:
                return False
            admins.append(user_id)
            await self.meta.update_one({"_id": "admins"}, {"$set": {"list": admins}}, upsert=True)
            return True
        except Exception as e:
            print("add_admin error:", e)
            return False

    async def remove_admin(self, user_id: int) -> bool:
        try:
            doc = await self.meta.find_one({"_id": "admins"})
            admins = doc.get("list", []) if doc else []
            if user_id not in admins:
                return False
            admins.remove(user_id)
            await self.meta.update_one({"_id": "admins"}, {"$set": {"list": admins}}, upsert=True)
            return True
        except Exception as e:
            print("remove_admin error:", e)
            return False

    async def get_admins(self) -> list[int]:
        try:
            doc = await self.meta.find_one({"_id": "admins"})
            return doc.get("list", []) if doc else []
        except Exception as e:
            print("get_admins error:", e)
            return []

    # Start Image
    async def set_start_image(self, url: str) -> bool:
        try:
            await self.meta.update_one({"_id": "start_img"}, {"$set": {"url": url}}, upsert=True)
            return True
        except Exception as e:
            print("set_start_image error:", e)
            return False

    async def get_start_image(self) -> str | None:
        try:
            doc = await self.meta.find_one({"_id": "start_img"})
            return doc.get("url") if doc else None
        except Exception as e:
            print("get_start_image error:", e)
            return None

    async def remove_start_image(self) -> bool:
        try:
            await self.meta.delete_one({"_id": "start_img"})
            return True
        except Exception as e:
            print("remove_start_image error:", e)
            return False

tb = Techifybots()
