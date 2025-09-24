"""
Redis service for managing distributed active tasks.
"""

import json
from typing import Dict, Any, Optional
import redis
from loguru import logger

from ...config.settings import settings
from ...models import TaskRequest, TaskResult, Plan


class ActiveTaskData:
    """Data structure for active task storage."""

    def __init__(self, request: TaskRequest, result: TaskResult, plan: Optional[Plan] = None):
        self.request = request
        self.result = result
        self.plan = plan

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "request": self.request.model_dump(mode='json'),
            "result": self.result.model_dump(mode='json'),
            "plan": self.plan.model_dump(mode='json') if self.plan else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActiveTaskData':
        """Create from dictionary after JSON deserialization."""
        request = TaskRequest(**data["request"])
        result = TaskResult(**data["result"])
        plan = Plan(**data["plan"]) if data.get("plan") else None
        return cls(request=request, result=result, plan=plan)


class RedisService:
    """Service for managing active tasks in Redis (Singleton pattern)."""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Implement singleton pattern to ensure only one Redis connection."""
        if cls._instance is None:
            cls._instance = super(RedisService, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of RedisService."""
        return cls()

    def __init__(self):
        if not self._initialized:
            self.redis_client = redis.Redis(
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.db,
                password=settings.redis.password,
                decode_responses=True
            )
            self.key_prefix = settings.redis.key_prefix
            self.ttl_seconds = settings.redis.ttl_seconds
            self.logger = logger

            # Test connection
            try:
                self.redis_client.ping()
                self.logger.info("Connected to Redis successfully")
            except redis.ConnectionError as e:
                self.logger.error(f"Failed to connect to Redis: {e}")
                raise

            # Mark as initialized
            self._initialized = True

    def _get_key(self, request_id: str) -> str:
        """Generate Redis key for a task."""
        return f"{self.key_prefix}{request_id}"

    def store_active_task(self, request_id: str, task_data: ActiveTaskData) -> None:
        """Store an active task in Redis."""
        try:
            key = self._get_key(request_id)
            data = task_data.to_dict()
            json_data = json.dumps(data)

            self.redis_client.setex(key, self.ttl_seconds, json_data)
            self.logger.debug(f"Stored active task: {request_id}")

        except Exception as e:
            self.logger.error(f"Failed to store active task {request_id}: {e}")
            raise

    def get_active_task(self, request_id: str) -> Optional[ActiveTaskData]:
        """Retrieve an active task from Redis."""
        try:
            key = self._get_key(request_id)
            json_data = self.redis_client.get(key)

            if json_data:
                data = json.loads(json_data)
                task_data = ActiveTaskData.from_dict(data)
                self.logger.debug(f"Retrieved active task: {request_id}")
                return task_data
            else:
                self.logger.debug(f"Active task not found: {request_id}")
                return None

        except Exception as e:
            self.logger.error(f"Failed to get active task {request_id}: {e}")
            return None

    def remove_active_task(self, request_id: str) -> bool:
        """Remove an active task from Redis."""
        try:
            key = self._get_key(request_id)
            result = self.redis_client.delete(key)

            if result > 0:
                self.logger.debug(f"Removed active task: {request_id}")
                return True
            else:
                self.logger.debug(f"Active task not found for removal: {request_id}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to remove active task {request_id}: {e}")
            return False

    def get_all_active_tasks(self) -> Dict[str, ActiveTaskData]:
        """Get all active tasks from Redis."""
        try:
            # Get all keys matching the prefix
            pattern = f"{self.key_prefix}*"
            keys = self.redis_client.keys(pattern)

            active_tasks = {}
            for key in keys:
                try:
                    json_data = self.redis_client.get(key)
                    if json_data:
                        data = json.loads(json_data)
                        task_data = ActiveTaskData.from_dict(data)

                        # Extract request_id from key
                        request_id = key.replace(self.key_prefix, "")
                        active_tasks[request_id] = task_data

                except Exception as e:
                    self.logger.error(f"Error processing active task key {key}: {e}")
                    continue

            self.logger.debug(f"Retrieved {len(active_tasks)} active tasks")
            return active_tasks

        except Exception as e:
            self.logger.error(f"Failed to get all active tasks: {e}")
            return {}

    def get_active_tasks_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get a summary of all active tasks (without full data for efficiency)."""
        try:
            active_tasks = self.get_all_active_tasks()
            summary = {}

            for request_id, task_data in active_tasks.items():
                summary[request_id] = {
                    "request_id": request_id,
                    "description": task_data.request.task_description,
                    "status": task_data.result.status,
                    "started_at": task_data.result.started_at,
                    "duration": task_data.result.calculate_duration()
                }

            return summary

        except Exception as e:
            self.logger.error(f"Failed to get active tasks summary: {e}")
            return {}

    def update_task_result(self, request_id: str, task_result: TaskResult) -> bool:
        """Update only the task result for an active task."""
        try:
            task_data = self.get_active_task(request_id)
            if task_data:
                task_data.result = task_result
                self.store_active_task(request_id, task_data)
                self.logger.debug(f"Updated task result for: {request_id}")
                return True
            else:
                self.logger.warning(f"Cannot update task result - active task not found: {request_id}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to update task result for {request_id}: {e}")
            return False

    def update_task_plan(self, request_id: str, plan: Plan) -> bool:
        """Update only the plan for an active task."""
        try:
            task_data = self.get_active_task(request_id)
            if task_data:
                task_data.plan = plan
                self.store_active_task(request_id, task_data)
                self.logger.debug(f"Updated task plan for: {request_id}")
                return True
            else:
                self.logger.warning(f"Cannot update task plan - active task not found: {request_id}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to update task plan for {request_id}: {e}")
            return False

    def get_active_task_count(self) -> int:
        """Get the count of active tasks."""
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis_client.keys(pattern)
            return len(keys)

        except Exception as e:
            self.logger.error(f"Failed to get active task count: {e}")
            return 0

    def cleanup_expired_tasks(self) -> int:
        """Clean up expired tasks (Redis TTL should handle this automatically, but this is a manual cleanup)."""
        # Since we're using TTL, expired keys are automatically removed
        # This method could be used for additional cleanup logic if needed
        return 0
