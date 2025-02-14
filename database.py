from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declarative_base

from sqlalchemy import Column, Integer, String, Boolean, Text, insert, select, update

from config import DATABASE_URL


class Base(DeclarativeBase):    
    def __repr__(self) -> str:
        cols = []
        for col in self.__table__.columns.keys():
            cols.append(f"{col} = {getattr(self, col)}")
        return f"<{self.__class__.__name__} {','.join(cols)}>"
    pass 

metadata = MetaData()

engine = create_async_engine(
    url = DATABASE_URL,
    # echo=True,  
)

async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_async_session():
    async with async_session() as session:
        yield session

async def create_tables(): 
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def drop_tables(): 
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

        

        
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    # "Логический" статус пользователя (не связанный с aiogram FSM)
    state = Column(String, default="Fine State")

    # Новое поле для хранения FSM‑состояний aiogram
    fsm_state = Column(String, default=None)

    balance = Column(Integer, default=0)
    interests = Column(String, nullable=True)
    correct_predict = Column(Boolean, default=False)
    feedback = Column(Text, nullable=True)
    feedback_character = Column(String, nullable=True)
    
    
async def get_user(session: AsyncSession, user_id: int):
    # async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        return result.scalars().first()
    
    
async def add_user(user_id: int, username: str, first_name: str, last_name: str):
    async with async_session() as session:
        user = User(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            balance=0
        )
        session.add(user)
        await session.commit()
        return user
    
async def get_user_without_session(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        return result.scalars().first()




async def update_user_state(session: AsyncSession, user_id: int, new_state: str):
    user: User = await get_user(session, user_id)
    if user:
        user.state = new_state
        await session.commit()


# ---- Обновляем конкретно FSM‑состояние в отдельном поле
async def update_user_fsm_state(session: AsyncSession, user_id: int, fsm_state: str):
    user: User = await get_user(session, user_id)
    if user:
        user.fsm_state = fsm_state
        await session.commit()




# # ---- Обновляем "логический" статус пользователя (не FSM)
# async def update_user_state(session, user_id: int, new_state: str):
#     async with async_session() as session:
#         user = await get_user(user_id)
#         if user:
#             user.state = new_state
#             await session.commit()


# # ---- Обновляем конкретно FSM‑состояние в отдельном поле
# async def update_user_fsm_state(user_id: int, fsm_state: str):
#     async with async_session() as session:
#         user = await get_user(user_id)
#         if user:
#             user.fsm_state = fsm_state
#             await session.commit()
