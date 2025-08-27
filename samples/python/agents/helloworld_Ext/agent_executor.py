from typing import Optional
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.utils.message import get_message_text
from greeting_style_extension import GreetingStyleExtension
from random_method_extension import RandomMethodExtension


# --8<-- [start:HelloWorldAgent]
class HelloWorldAgent:
    """Hello World Agent."""

    async def invoke(self) -> str:
        return 'Hello World'


# --8<-- [end:HelloWorldAgent]


# --8<-- [start:HelloWorldAgentExecutor_init]
class HelloWorldAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation with Greeting Style Extension support."""

    def __init__(self, greeting_extension: Optional[GreetingStyleExtension] = None, random_method_extension: Optional[RandomMethodExtension] = None):
        self.agent = HelloWorldAgent()
        self.greeting_extension = greeting_extension
        self.random_method_extension = random_method_extension

    # --8<-- [end:HelloWorldAgentExecutor_init]
    # --8<-- [start:HelloWorldAgentExecutor_execute]
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        message_text = get_message_text(context.message) if context.message else ""
        message_text_lower = message_text.lower()
        
        # Check if random method extension should be activated
        if self.random_method_extension and self._is_random_method_active(context, message_text_lower):
            # Extract parameters from message or metadata
            params = self._extract_random_method_parameters(context, message_text_lower)
            response = self.random_method_extension.handle_random_method(params)
            
            if 'error' in response:
                result = f"Error: {response['error']['message']}"
            else:
                # Extract the greeting text from the response
                result = response['parts'][0]['text']
                # Add metadata info to the response
                metadata = response.get('metadata', {}).get('randomSelection', {})
                if metadata:
                    result += f" [Style: {metadata.get('style', 'unknown')}, Language: {metadata.get('language', 'unknown')}]"
        
        # Check if greeting style extension is available
        elif self.greeting_extension:
            # Check for proper A2A extension activation first
            extension_active = self._is_extension_active_from_headers(context)
            extension_params = self._extract_extension_parameters_from_metadata(context)
            
            if extension_active and extension_params:
                # Use proper A2A extension parameters
                style = extension_params.get('style', 'casual')
                language = extension_params.get('language', 'en')
                result = self.greeting_extension.get_greeting(style=style, language=language)
            else:
                # Fallback to keyword-based activation for demo compatibility
                style = 'casual'
                language = 'en'
                
                # Extract style from message text
                if 'formal' in message_text_lower:
                    style = 'formal'
                elif 'enthusiastic' in message_text_lower:
                    style = 'enthusiastic'
                elif 'multilingual' in message_text_lower:
                    style = 'multilingual'
                
                # Extract language from message text
                if 'spanish' in message_text_lower or 'español' in message_text_lower:
                    language = 'es'
                elif 'french' in message_text_lower or 'français' in message_text_lower:
                    language = 'fr'
                elif 'german' in message_text_lower or 'deutsch' in message_text_lower:
                    language = 'de'
                elif 'japanese' in message_text_lower or '日本語' in message_text_lower:
                    language = 'ja'
                
                # Use extension if keywords found, otherwise fallback
                if any(keyword in message_text_lower for keyword in ['formal', 'enthusiastic', 'multilingual', 'casual', 'spanish', 'french', 'german', 'japanese']):
                    result = self.greeting_extension.get_greeting(style=style, language=language)
                else:
                    result = await self.agent.invoke()
        else:
            # Fall back to default behavior
            result = await self.agent.invoke()
            
        await event_queue.enqueue_event(new_agent_text_message(result))

    def _is_random_method_active(self, context: RequestContext, message_text: str) -> bool:
        """Check if the random method extension should be activated."""
        # Check for extension header activation
        if hasattr(context, 'active_extensions'):
            active_extensions = getattr(context, 'active_extensions', [])
            if self.random_method_extension.extension_uri in active_extensions:
                return True
        
        # Check for keyword-based activation in message text
        random_keywords = ['random greeting', 'surprise me', 'random hello', 'generate random']
        return any(keyword in message_text for keyword in random_keywords)
    
    def _extract_random_method_parameters(self, context: RequestContext, message_text: str) -> dict:
        """Extract parameters for the random method from context and message."""
        params = {'id': getattr(context, 'task_id', 'random-task')}
        
        # Check message metadata first
        if hasattr(context, 'message') and context.message:
            metadata = getattr(context.message, 'metadata', None)
            if metadata:
                extensions_metadata = metadata.get('extensions', {})
                extension_params = extensions_metadata.get(self.random_method_extension.extension_uri, {})
                if extension_params:
                    params.update(extension_params)
                    return params
        
        # Parse exclusions from message text
        exclude_styles = []
        exclude_languages = []
        
        if 'no formal' in message_text or 'not formal' in message_text:
            exclude_styles.append('formal')
        if 'no enthusiastic' in message_text or 'not enthusiastic' in message_text:
            exclude_styles.append('enthusiastic')
        if 'no casual' in message_text or 'not casual' in message_text:
            exclude_styles.append('casual')
        if 'no multilingual' in message_text or 'not multilingual' in message_text:
            exclude_styles.append('multilingual')
            
        if 'no english' in message_text or 'not english' in message_text:
            exclude_languages.append('en')
        if 'no spanish' in message_text or 'not spanish' in message_text:
            exclude_languages.append('es')
        if 'no french' in message_text or 'not french' in message_text:
            exclude_languages.append('fr')
        if 'no german' in message_text or 'not german' in message_text:
            exclude_languages.append('de')
        if 'no japanese' in message_text or 'not japanese' in message_text:
            exclude_languages.append('ja')
            
        if exclude_styles:
            params['excludeStyles'] = exclude_styles
        if exclude_languages:
            params['excludeLanguages'] = exclude_languages
            
        return params

    # --8<-- [end:HelloWorldAgentExecutor_execute]

    def _is_extension_active_from_headers(self, context: RequestContext) -> bool:
        """Check if the greeting style extension is active based on request headers."""
        # Check if extension is in the active extensions list from X-A2A-Extensions header
        # This would be set by the A2A framework based on the header
        active_extensions = getattr(context, 'active_extensions', [])
        extension_uri = self.greeting_extension.extension_uri
        return extension_uri in active_extensions if active_extensions else False
    
    def _extract_extension_parameters_from_metadata(self, context: RequestContext) -> dict:
        """Extract extension parameters from message metadata."""
        if not hasattr(context, 'message') or not context.message:
            return {}
            
        metadata = getattr(context.message, 'metadata', {})
        if not metadata:
            return {}
            
        extensions_metadata = metadata.get('extensions', {})
        extension_uri = self.greeting_extension.extension_uri
        
        return extensions_metadata.get(extension_uri, {})
    
    def get_supported_methods(self) -> list:
        """Get list of supported custom methods."""
        methods = []
        if self.random_method_extension:
            methods.append("message/random")
        return methods

    # --8<-- [start:HelloWorldAgentExecutor_cancel]
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')

    # --8<-- [end:HelloWorldAgentExecutor_cancel]
