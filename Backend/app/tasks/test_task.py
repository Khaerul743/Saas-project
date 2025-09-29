from typing import Optional

from sqlalchemy.orm import Session

from app.configs.database import SessionLocal
from app.events.loop_manager import run_async
from app.events.redis_event import Event, EventType, event_bus
from app.tasks import celery_app
from app.utils.logger import get_logger
from app.utils.event_utils import publish_agent_event

logger = get_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.agent_task.create_simple_rag_agent")
def test_task(self, file_data: Optional[dict], agent_data: dict, user_id: int):
    task_id = self.request.id
    db = SessionLocal()
    logger.info(f"Task Execution: user_id {user_id}")

    progress = _update_progress(self, 20, status="Initialize agent")
    publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
    progress = _update_progress(self, 40, status="Initialize agent")
    publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
    progress = _update_progress(self, 60, status="Initialize agent")
    publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
    progress = _update_progress(self, 80, status="Initialize agent")
    publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
    progress = _update_progress(self, 100, status="Initialize agent")
    publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
    return {"Message": "Successfully"}


def _update_progress(task_instance, current: int, status: str, state: str = "PROGRESS"):
    """Update task progress"""
    task_instance.update_state(
        state=state, meta={"current": current, "total": 100, "status": status}
    )

    return {"current": current, "total": 100, "status": status}
