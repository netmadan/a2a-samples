import os
from beeai_framework.adapters.a2a import A2AServer, A2AServerConfig
from beeai_framework.agents.experimental import RequirementAgent
from beeai_framework.backend import ChatModel
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.serve.utils import LRUMemoryManager
from beeai_framework.tools.search.duckduckgo import DuckDuckGoSearchTool
from beeai_framework.tools.search.wikipedia import WikipediaTool
from beeai_framework.tools.think import ThinkTool
from beeai_framework.tools.weather import OpenMeteoTool


def main() -> None:
    llm = ChatModel.from_name(os.environ.get("BEEAI_MODEL", "ollama:granite3.3:8b"))
    agent = RequirementAgent(
        llm=llm,
        tools=[ThinkTool(), DuckDuckGoSearchTool(), OpenMeteoTool(), WikipediaTool()],
        memory=UnconstrainedMemory(),
    )

    # Register the agent with the A2A server and run the HTTP server
    # For the ToolCallingAgent, we dont need to specify ACPAgent factory method
    # because it is already registered in the A2AServer
    # we use LRU memory manager to keep limited amount of sessions in the memory
    A2AServer(config=A2AServerConfig(port=int(os.environ.get("A2A_PORT", 9999))), memory_manager=LRUMemoryManager(maxsize=100)).register(agent).serve()


if __name__ == "__main__":
    main()
