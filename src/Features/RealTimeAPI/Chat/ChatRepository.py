import uuid
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from Domain.base_entities import Messages
from SharedKernel.persistence.CrudRepository import CrudRepository
from SharedKernel.persistence.PersistenceManager import get_db_session

class ChatRepository(CrudRepository[Messages, uuid.UUID]):
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        super().__init__(Messages, session)


