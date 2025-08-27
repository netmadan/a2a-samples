from typing import Optional
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.utils.message import get_message_text
from time_greeting_extension import TimeGreetingExtension


# --8<-- [start:HelloWorldAgent]
class HelloWorldAgent:
    """Hello World Agent."""

    async def invoke(self) -> str:
        return 'Hello World'


# --8<-- [end:HelloWorldAgent]


# --8<-- [start:HelloWorldAgentExecutor_init]
class HelloWorldAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation with Time Greeting Extension support."""

    def __init__(self, time_greeting_extension: Optional[TimeGreetingExtension] = None):
        self.agent = HelloWorldAgent()
        self.time_greeting_extension = time_greeting_extension

    # --8<-- [end:HelloWorldAgentExecutor_init]
    # --8<-- [start:HelloWorldAgentExecutor_execute]
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        message_text = get_message_text(context.message) if context.message else ""
        message_text_lower = message_text.lower()
        
        # Check if time greeting extension should be activated
        if self.time_greeting_extension and self._is_time_greeting_active(context, message_text_lower):
            # Extract parameters from message or metadata
            params = self._extract_time_greeting_parameters(context, message_text_lower)
            response = self.time_greeting_extension.handle_time_greeting_method(params)
            
            if 'error' in response:
                result = f"Error: {response['error']['message']}"
            else:
                # Extract the greeting text from the response
                result = response['parts'][0]['text']
        else:
            # Fall back to default behavior
            result = await self.agent.invoke()
            
        await event_queue.enqueue_event(new_agent_text_message(result))

    # --8<-- [end:HelloWorldAgentExecutor_execute]

    # --8<-- [start:HelloWorldAgentExecutor_cancel]
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')

    # --8<-- [end:HelloWorldAgentExecutor_cancel]
    
    def _is_time_greeting_active(self, context: RequestContext, message_text: str) -> bool:
        """Check if the time greeting extension should be activated."""
        # Check for extension header activation
        if hasattr(context, 'active_extensions'):
            active_extensions = getattr(context, 'active_extensions', [])
            if self.time_greeting_extension.extension_uri in active_extensions:
                return True
        
        # Check for keyword-based activation in message text
        time_keywords = [
            'time greeting', 'good morning', 'good afternoon', 'good evening',
            'what time is it', 'current time greeting', 'greet me based on time',
            'time based greeting', 'greeting with time'
        ]
        return any(keyword in message_text for keyword in time_keywords)
    
    def _extract_time_greeting_parameters(self, context: RequestContext, message_text: str) -> dict:
        """Extract parameters for the time greeting method from context and message."""
        params = {'id': getattr(context, 'task_id', 'time-greeting-task')}
        
        # Check message metadata first for proper A2A extension parameters
        if hasattr(context, 'message') and context.message:
            metadata = getattr(context.message, 'metadata', None)
            if metadata:
                extensions_metadata = metadata.get('extensions', {})
                extension_params = extensions_metadata.get(self.time_greeting_extension.extension_uri, {})
                if extension_params:
                    params.update(extension_params)
                    return params
        
        # Parse parameters from natural language in message text
        # Timezone detection
        timezone_mappings = {
            'utc': 'UTC',
            'gmt': 'GMT', 
            'new york': 'America/New_York',
            'los angeles': 'America/Los_Angeles',
            'london': 'Europe/London',
            'paris': 'Europe/Paris',
            'tokyo': 'Asia/Tokyo',
            'sydney': 'Australia/Sydney'
        }
        
        for location, tz in timezone_mappings.items():
            if location in message_text:
                params['timezone'] = tz
                break
        
        # Style detection
        if 'formal' in message_text:
            params['style'] = 'formal'
        elif 'brief' in message_text:
            params['style'] = 'brief'
        else:
            params['style'] = 'casual'
        
        # Language detection
        language_mappings = {
            'spanish': 'es', 'español': 'es',
            'french': 'fr', 'français': 'fr',
            'german': 'de', 'deutsch': 'de',
            'japanese': 'ja', '日本語': 'ja'
        }
        
        for lang_word, lang_code in language_mappings.items():
            if lang_word in message_text:
                params['language'] = lang_code
                break
        
        # Time format detection
        if '24 hour' in message_text or '24h' in message_text or 'military time' in message_text:
            params['format'] = '24h'
        
        # Include time detection
        if 'no time' in message_text or 'without time' in message_text:
            params['includeTime'] = False
            
        return params
