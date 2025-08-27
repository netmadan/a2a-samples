"""Greeting Style Extension for HelloWorld Agent.

This extension allows clients to customize greeting styles including:
- Different formality levels (casual, formal, enthusiastic)
- Multiple languages support
- Custom greeting templates
"""

from typing import Dict, Any, Optional
from a2a.types import AgentCard


class GreetingStyleExtension:
    """Extension that provides customizable greeting styles and languages."""
    
    EXTENSION_URI = "http://localhost:8080/extensions/greeting-style/v1"
    
    def __init__(self):
        """Initialize the greeting style extension with predefined greetings."""
        self._greetings = {
            "casual": {
                "en": "Hey there! 👋",
                "es": "¡Hola! 👋",
                "fr": "Salut! 👋",
                "de": "Hallo! 👋",
                "ja": "こんにちは！ 👋"
            },
            "formal": {
                "en": "Good day. I am pleased to make your acquaintance.",
                "es": "Buenos días. Es un placer conocerle.",
                "fr": "Bonjour. Je suis ravi de faire votre connaissance.",
                "de": "Guten Tag. Es freut mich, Sie kennenzulernen.",
                "ja": "こんにちは。お会いできて光栄です。"
            },
            "enthusiastic": {
                "en": "HELLO THERE!!! 🎉✨ Welcome to the amazing world of A2A!",
                "es": "¡¡¡HOLA!!! 🎉✨ ¡Bienvenido al increíble mundo de A2A!",
                "fr": "BONJOUR!!! 🎉✨ Bienvenue dans le monde merveilleux d'A2A!",
                "de": "HALLO!!! 🎉✨ Willkommen in der fantastischen Welt von A2A!",
                "ja": "こんにちは！！！ 🎉✨ A2Aの素晴らしい世界へようこそ！"
            },
            "multilingual": {
                "en": "Hello (English) • Hola (Español) • Bonjour (Français) • Hallo (Deutsch) • こんにちは (日本語)",
                "es": "Hello (English) • Hola (Español) • Bonjour (Français) • Hallo (Deutsch) • こんにちは (日本語)",
                "fr": "Hello (English) • Hola (Español) • Bonjour (Français) • Hallo (Deutsch) • こんにちは (日本語)",
                "de": "Hello (English) • Hola (Español) • Bonjour (Français) • Hallo (Deutsch) • こんにちは (日本語)",
                "ja": "Hello (English) • Hola (Español) • Bonjour (Français) • Hallo (Deutsch) • こんにちは (日本語)"
            }
        }
        
        self._supported_styles = list(self._greetings.keys())
        self._supported_languages = ["en", "es", "fr", "de", "ja"]
        self._default_style = "casual"
        self._default_language = "en"

    @property
    def extension_uri(self) -> str:
        """Return the unique URI identifier for this extension."""
        return self.EXTENSION_URI

    def get_extension_metadata(self) -> Dict[str, Any]:
        """Return metadata about this extension for the AgentCard."""
        return {
            "name": "Greeting Style Extension",
            "description": "Customize greeting styles and languages",
            "version": "1.0.0",
            "supported_styles": self._supported_styles,
            "supported_languages": self._supported_languages,
            "default_style": self._default_style,
            "default_language": self._default_language,
            "examples": [
                {"style": "casual", "language": "en"},
                {"style": "formal", "language": "fr"},
                {"style": "enthusiastic", "language": "ja"},
                {"style": "multilingual", "language": "en"}
            ]
        }

    def extend_agent_card(self, agent_card: AgentCard) -> AgentCard:
        """Extend the agent card with greeting style extension capabilities."""
        # Create a copy of the agent card to avoid modifying the original
        extended_card = agent_card.model_copy()
        
        # Add extension to capabilities if not already present
        if not hasattr(extended_card.capabilities, 'extensions') or extended_card.capabilities.extensions is None:
            extended_card.capabilities.extensions = {}
        
        # Add our extension metadata
        extended_card.capabilities.extensions[self.extension_uri] = self.get_extension_metadata()
        
        return extended_card

    def get_greeting(self, style: str = None, language: str = None) -> str:
        """
        Get a greeting based on the specified style and language.
        
        Args:
            style: The greeting style ('casual', 'formal', 'enthusiastic', 'multilingual')
            language: The language code ('en', 'es', 'fr', 'de', 'ja')
            
        Returns:
            A formatted greeting string
        """
        # Use defaults if not specified
        style = style or self._default_style
        language = language or self._default_language
        
        # Validate style
        if style not in self._supported_styles:
            style = self._default_style
        
        # Validate language
        if language not in self._supported_languages:
            language = self._default_language
            
        # Get the greeting
        try:
            return self._greetings[style][language]
        except KeyError:
            # Fallback to default if specific combination not found
            return self._greetings[self._default_style][self._default_language]

    def parse_extension_parameters(self, message_metadata: Dict[str, Any]) -> Dict[str, str]:
        """
        Parse extension parameters from message metadata.
        
        Args:
            message_metadata: Metadata from the incoming message
            
        Returns:
            Dictionary with 'style' and 'language' parameters
        """
        params = {}
        
        if message_metadata:
            # Look for extension parameters in metadata
            extension_params = message_metadata.get('extensions', {}).get(self.extension_uri, {})
            
            params['style'] = extension_params.get('style', self._default_style)
            params['language'] = extension_params.get('language', self._default_language)
        else:
            params['style'] = self._default_style
            params['language'] = self._default_language
            
        return params

    def is_extension_active(self, active_extensions: list) -> bool:
        """Check if this extension is active in the current request."""
        return self.extension_uri in active_extensions if active_extensions else False