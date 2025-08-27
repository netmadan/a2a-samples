import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent_executor import (
    HelloWorldAgentExecutor,  # type: ignore[import-untyped]
)
from time_greeting_extension import TimeGreetingExtension


if __name__ == '__main__':
    # Create time greeting extension
    time_greeting_extension = TimeGreetingExtension()
    # --8<-- [start:AgentSkill]
    skill = AgentSkill(
        id='hello_world',
        name='Returns hello world',
        description='just returns hello world',
        tags=['hello world'],
        examples=['hi', 'hello world'],
    )
    # --8<-- [end:AgentSkill]

    extended_skill = AgentSkill(
        id='super_hello_world',
        name='Returns a SUPER Hello World',
        description='A more enthusiastic greeting, only for authenticated users.',
        tags=['hello world', 'super', 'extended'],
        examples=['super hi', 'give me a super hello'],
    )
    
    # Add skill for the time greeting extension
    time_greeting_skill = AgentSkill(
        id='time_greeting',
        name='Time-Based Greeting Generator',
        description='Generate contextually appropriate greetings based on current time of day with timezone and language support.',
        tags=['greeting', 'time', 'timezone', 'multilingual', 'extension'],
        examples=[
            'time greeting',
            'good morning',
            'time greeting in Tokyo',
            'formal time greeting in Spanish',
            'what time is it'
        ],
    )

    # --8<-- [start:AgentCard]
    # This will be the public-facing agent card
    public_agent_card = AgentCard(
        name='Hello World Agent',
        description='Just a hello world agent',
        url='http://localhost:9999/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill, time_greeting_skill],  # Include time greeting skill
        supports_authenticated_extended_card=True,
    )
    # --8<-- [end:AgentCard]
    
    # Add time greeting extension to agent card capabilities
    time_extension_metadata = time_greeting_extension.get_extension_metadata()
    if not hasattr(public_agent_card.capabilities, 'extensions') or public_agent_card.capabilities.extensions is None:
        public_agent_card.capabilities.extensions = {}
    
    # Add time greeting extension to the extensions dict
    public_agent_card.capabilities.extensions[time_extension_metadata["uri"]] = time_extension_metadata

    # This will be the authenticated extended agent card
    # It includes the additional 'extended_skill'
    specific_extended_agent_card = public_agent_card.model_copy(
        update={
            'name': 'Hello World Agent - Extended Edition',  # Different name for clarity
            'description': 'The full-featured hello world agent for authenticated users.',
            'version': '1.0.1',  # Could even be a different version
            # Capabilities and other fields like url, default_input_modes, default_output_modes,
            # supports_authenticated_extended_card are inherited from public_agent_card unless specified here.
            'skills': [
                skill,
                extended_skill,
                time_greeting_skill,
            ],  # All skills for the extended card
        }
    )
    
    # Add time greeting extension to extended card capabilities
    if not hasattr(specific_extended_agent_card.capabilities, 'extensions') or specific_extended_agent_card.capabilities.extensions is None:
        specific_extended_agent_card.capabilities.extensions = {}
    
    # Add time greeting extension to the extensions dict
    specific_extended_agent_card.capabilities.extensions[time_extension_metadata["uri"]] = time_extension_metadata

    request_handler = DefaultRequestHandler(
        agent_executor=HelloWorldAgentExecutor(
            time_greeting_extension=time_greeting_extension
        ),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
        extended_agent_card=specific_extended_agent_card,
    )

    uvicorn.run(server.build(), host='0.0.0.0', port=9999)
