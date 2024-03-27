from beanie import init_beanie
import motor.motor_asyncio
from .models.user import User
import os
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv('MONGO_HOST_URI')

async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        f"mongodb://{mongo_uri}:27017"
    )
    #replace localhost with database container name to connect it.
    await init_beanie(database=client.LD, document_models=[User])
    print('database connected with mongoDB')