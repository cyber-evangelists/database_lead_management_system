from beanie import init_beanie
import motor.motor_asyncio
from .models.user import User


async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://localhost:27017/"
    )
    #replace localhost with database container name to connect it.
    await init_beanie(database=client.LD, document_models=[User])
    print('database connected with mongoDB')