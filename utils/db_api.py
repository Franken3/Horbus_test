import json
import os
from copy import copy
from sqlalchemy import select
from typing import Any, Sequence, List, Tuple

from dotenv import load_dotenv
from sqlalchemy import delete, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from data.models import Users, Base, Subscriptions, Posts, Digests, AvailableSubscriptions

load_dotenv()
alchemy_engine = str(os.getenv("ALCHEMY_ENGINE"))


async def create_session():
    async_engine = create_async_engine(alchemy_engine)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return AsyncSession(async_engine)


# Создание нового пользователя
async def create_new_or_get_user(TgId: int, Name: str) -> Users:
    async with await create_session() as session:
        existing_user_stmp = select(Users).where(Users.tgid == TgId)
        existing_user_res = await session.execute(existing_user_stmp)
        existing_user = existing_user_res.scalar_one_or_none()
        if existing_user:
            return existing_user

        new_user = Users(
            tgid=TgId,
            name=Name
        )
        session.add(new_user)
        await session.flush()
        ret_user = copy(new_user)
        await session.commit()

    return ret_user

# Получение подписок
async def get_user_subscriptions(user_id: int) -> Sequence[Row | RowMapping | Any]:
    async with await create_session() as session:
        subscriptions_stmp = select(Subscriptions).where(Subscriptions.user_id == user_id)
        subscriptions_res = await session.execute(subscriptions_stmp)
        subscriptions = subscriptions_res.scalars().all()
    return subscriptions

async def get_user_subscription_status(user_id: int) -> List[Tuple]:
    async with await create_session() as session:
        user_subscriptions = await get_user_subscriptions(user_id)
        user_subscription_sources = [sub.source_name for sub in user_subscriptions]

        all_subscriptions_stmp = select(AvailableSubscriptions)
        all_subscriptions_res = await session.execute(all_subscriptions_stmp)
        all_subscriptions = all_subscriptions_res.scalars().all()

        subscriptions_status = []
        for sub in all_subscriptions:
            status = '✅' if sub.source_name in user_subscription_sources else '❌'
            subscriptions_status.append((f'{sub.source_name}  {status}',
                                         True if sub.source_name in user_subscription_sources else False, sub.id))

    return subscriptions_status
# Подписать и отписать пользователя
async def subscribe_user(user_id: int, subscription_id: int, sub: bool) -> Sequence[Row | RowMapping | Any]:
    async with await create_session() as session:
        subscriptions_stmp = select(AvailableSubscriptions).where(
            AvailableSubscriptions.id == subscription_id)
        subscriptions_res = await session.execute(subscriptions_stmp)
        subscriptions = subscriptions_res.scalar_one()
        if sub:
            new_subscription = Subscriptions(
                user_id=user_id,
                source_name=subscriptions.source_name
            )
            session.add(new_subscription)
        else:
            stmp = delete(Subscriptions).where(Subscriptions.user_id == user_id,
                                               Subscriptions.source_name == subscriptions.source_name)
            await session.execute(stmp)

        await session.flush()
        subscriptions_stmp = select(Subscriptions).where(Subscriptions.user_id == user_id)
        subscriptions_res = await session.execute(subscriptions_stmp)
        subscriptions = copy(subscriptions_res.scalars().all())
        await session.commit()

    return subscriptions


# Создание дайджеста
async def create_digest(user_id: int) -> Digests:
    async with await create_session() as session:
        #тк я немного не правильно понял тз, то пришлось накостылить чуть-чуть
        subscriptions = await get_user_subscriptions(user_id)
        sub_source_names = [sub.source_name for sub in subscriptions]

        sub_stmp = select(AvailableSubscriptions.id).where(AvailableSubscriptions.source_name.in_(sub_source_names))
        sub_res = await session.execute(sub_stmp)
        pre_sub_ids = sub_res.fetchall()
        sub_ids = [sub[0] for sub in pre_sub_ids]

        posts_tmp = select(Posts).where((Posts.subscription_id.in_(sub_ids)) & (Posts.popularity > 250))
        posts_res = await session.execute(posts_tmp)
        posts = posts_res.scalars().all()
        new_digest = Digests(
            user_id=user_id,
            posts=json.dumps([{"id": post.id, "popularity": post.popularity} for post in posts])
        )

        session.add(new_digest)
        await session.flush()
        text = ''
        i = 0
        for p in posts:
            i += 1
            text += f'<b>{i}:</b> {p.content} \n\n'

        await session.commit()

    return text

