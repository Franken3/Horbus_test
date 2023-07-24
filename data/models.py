import asyncio
import os
from random import choice, randint
from typing import List

from dotenv import load_dotenv
from sqlalchemy import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, relationship

load_dotenv()
alchemy_engine = str(os.getenv("ALCHEMY_ENGINE"))


class Base(DeclarativeBase): pass


async def create_session():
    async_engine = create_async_engine(alchemy_engine)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return AsyncSession(async_engine)


class Users(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    tgid = Column(BigInteger, nullable=False)


class Subscriptions(Base):
    __tablename__ = "Subscriptions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)


class Posts(Base):
    __tablename__ = "Posts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subscription_id = Column(Integer, ForeignKey("AvailableSubscriptions.id"), nullable=False)
    content = Column(String, nullable=False)
    popularity = Column(Integer, nullable=False)


class AvailableSubscriptions(Base):
    __tablename__ = "AvailableSubscriptions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_name = Column(String, nullable=False)


class Digests(Base):
    __tablename__ = "Digests"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    posts = Column(JSON, nullable=False)



async def create_all():
    async_engine = create_async_engine(alchemy_engine)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return AsyncSession(async_engine)

async def populate_available_subscriptions(names: List[str]):
    async with await create_session() as session:
        for name in names:
            subscription = AvailableSubscriptions(source_name=name)
            session.add(subscription)
        await session.commit()


async def create_posts(post_contents: List[str]):
    async with await create_session() as session:
        subs_stmp = select(AvailableSubscriptions)
        subs_res = await session.execute(subs_stmp)
        subscriptions = subs_res.scalars().all()

        for content in post_contents:
            chosen_sub = choice(subscriptions)

            new_post = Posts(
                subscription_id=chosen_sub.id,
                content=content,
                popularity=randint(1, 500)
            )

            session.add(new_post)

        await session.commit()

if __name__ == "__main__":
    try:
        asyncio.run(create_all())
        subscription_names = ["News Source 1", "News Source 2", "Blog 1", "Blog 2", "Magazine 1", "Magazine 2",
                              "Forum 1", "Forum 2", "Podcast 1", "Podcast 2"]
        post_contents = [
            "Солнечный день наступает после дождя.",
            "Луна светит ярче, когда ночь темна.",
            "Счастье находится не в вещах, а в нас самих.",
            "Смелость не всегда ревет. Иногда она тихий голос в конце дня, говорящий: я попробую снова завтра.",
            "Не важно, как медленно ты идешь, до тех пор пока ты не остановишься.",
            "Успех — это способность терпеть поражение за поражением без потери энтузиазма.",
            "Иногда самый лучший способ решить проблему - это перестать ее избегать.",
            "Трудности и препятствия - это важные шаги на пути к успеху.",
            "Величайшая слава в жизни - не в том, чтобы никогда не падать, а в том, чтобы каждый раз подниматься после падения.",
            "Успех - это не ключ к счастью. Счастье - это ключ к успеху. Если вы любите то, что делаете, вы будете успешны.",
            "У меня есть вопросы к моему коту. Почему он всегда смотрит на меня, когда я ем?",
            "Вечеринка без торта - это просто собрание.",
            "Мое кофе должно быть, как я: темным, сильным и горьким.",
            "Все говорят, что смех - лучшее лекарство. Моё здоровье, видимо, не в курсе.",
            "Если бы моя жизнь была фильмом, название было бы 'Поиск удаленного управления'.",
            "Бегите, ведь калории считают нас за сладости!",
            "Если бы у меня был доллар за каждый раз, когда я что-то потерял, я бы, вероятно, потерял и эти доллары.",
            "Мое терпение исчезает быстрее, чем батарейка на моем телефоне.",
            "Тот момент, когда вы уже открыли холодильник в третий раз, но еда все еще не появилась.",
            "Мой вес не проблема, проблема в моем любимом кексе!",

        ]

        asyncio.run(populate_available_subscriptions(subscription_names))
        asyncio.run(create_posts(post_contents=post_contents))
        print('Таблицы создал - все круто')
    except Exception as e:
        print(f'Подготовка таблиц: {e}')
