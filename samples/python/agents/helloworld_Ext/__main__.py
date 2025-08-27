import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentExtension,
    AgentSkill,
)
from agent_executor import (
    HelloWorldAgentExecutor,  # type: ignore[import-untyped]
)
from greeting_style_extension import GreetingStyleExtension
from random_method_extension import RandomMethodExtension


if __name__ == '__main__':
    # Create both extensions
    greeting_extension = GreetingStyleExtension()
    random_method_extension = RandomMethodExtension()
    
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
    
    # Add a new skill for the greeting style extension
    greeting_style_skill = AgentSkill(
        id='greeting_style',
        name='Customizable Greeting Styles',
        description='Get greetings in different styles and languages using the greeting style extension.',
        tags=['greeting', 'style', 'multilingual', 'extension'],
        examples=[
            'formal greeting in French',
            'enthusiastic hello in Japanese',
            'casual greeting in Spanish',
            'multilingual greeting'
        ],
    )
    
    # Add skill for the random method extension
    random_method_skill = AgentSkill(
        id='random_greeting',
        name='Random Greeting Generator',
        description='Generate random greetings with random style and language combinations using the message/random method.',
        tags=['random', 'greeting', 'method', 'extension'],
        examples=[
            'Generate a random greeting',
            'Random hello with some exclusions',
            'Surprise me with a greeting'
        ],
    )

    # --8<-- [start:AgentCard]
    # This will be the public-facing agent card
    public_agent_card = AgentCard(
        name='Hello World Agent',
        description='Just a hello world agent with greeting style extension support',
        url='http://localhost:9999/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill, greeting_style_skill, random_method_skill],  # Include all skills
        supports_authenticated_extended_card=True,
    )
    
    # Apply both extensions to the agent card
    public_agent_card = greeting_extension.extend_agent_card(public_agent_card)
    # Add random method extension metadata to capabilities
    random_extension_metadata = random_method_extension.get_extension_metadata()
    
    # Ensure extensions dict exists
    if not hasattr(public_agent_card.capabilities, 'extensions') or public_agent_card.capabilities.extensions is None:
        public_agent_card.capabilities.extensions = {}
    
    # Add random method extension to the extensions dict
    public_agent_card.capabilities.extensions[random_extension_metadata["uri"]] = random_extension_metadata
    # --8<-- [end:AgentCard]

    # This will be the authenticated extended agent card
    # It includes the additional 'extended_skill'
    specific_extended_agent_card = public_agent_card.model_copy(
        update={
            'name': 'Hello World Agent - Extended Edition',  # Different name for clarity
            'description': 'The full-featured hello world agent for authenticated users with greeting style extension.',
            'version': '1.0.1',  # Could even be a different version
            # Capabilities and other fields like url, default_input_modes, default_output_modes,
            # supports_authenticated_extended_card are inherited from public_agent_card unless specified here.
            'skills': [
                skill,
                extended_skill,
                greeting_style_skill,
                random_method_skill,
            ],  # All skills for the extended card
        }
    )
    
    # Apply both extensions to the extended card as well
    specific_extended_agent_card = greeting_extension.extend_agent_card(specific_extended_agent_card)
    # Add random method extension metadata to capabilities
    if not hasattr(specific_extended_agent_card.capabilities, 'extensions') or specific_extended_agent_card.capabilities.extensions is None:
        specific_extended_agent_card.capabilities.extensions = {}
    
    # Add random method extension to the extensions dict
    specific_extended_agent_card.capabilities.extensions[random_extension_metadata["uri"]] = random_extension_metadata

    request_handler = DefaultRequestHandler(
        agent_executor=HelloWorldAgentExecutor(
            greeting_extension=greeting_extension,
            random_method_extension=random_method_extension
        ),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
        extended_agent_card=specific_extended_agent_card,
    )

    uvicorn.run(server.build(), host='0.0.0.0', port=9999)
