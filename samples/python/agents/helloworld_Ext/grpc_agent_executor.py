from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError


class HelloWorldAgent:
    """Hello World Agent for gRPC."""

    async def invoke(self) -> str:
        return 'Hello World from gRPC!'

    async def stream(self, query: str, context_id: str):
        """Stream the response for gRPC compatibility."""
        # Simulate streaming by yielding partial results
        yield False, "Hello"
        yield False, " World"
        yield True, " from gRPC!"


class HelloWorldGrpcAgentExecutor(AgentExecutor):
    """gRPC-based HelloWorld Agent Executor."""

    def __init__(self):
        self.agent = HelloWorldAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        task = context.current_task

        # This agent produces Task objects for gRPC compatibility
        if not task:
            task = new_task(context.message)  # type: ignore
            await event_queue.enqueue_event(task)
        
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        
        # Use streaming results for gRPC
        async for finished, text in self.agent.stream(query, task.context_id):
            if not finished:
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(text, task.context_id, task.id),
                )
                continue
            
            # Emit the final result
            await updater.add_artifact(
                [Part(root=TextPart(text=text))],
                name='response',
            )
            await updater.complete()
            break

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise ServerError(error=UnsupportedOperationError())