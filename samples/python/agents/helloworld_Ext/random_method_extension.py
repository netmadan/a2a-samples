#!/usr/bin/env python3
"""
Random Greeting Method Extension for A2A Protocol.
This extension implements the message/random JSON-RPC method.
"""

import json
import random
import uuid
from typing import Optional, Dict, List, Any


class RandomMethodExtension:
    """Implementation of the message/random method extension."""
    
    def __init__(self):
        self.extension_uri = "http://localhost:8080/extensions/random-greeting-method/v1"
        self.method_name = "message/random"
        
        # Same greeting data as the greeting style extension
        self._greetings = {
            "casual": {
                "en": "Hey there! 👋",
                "es": "¡Hola! 👋", 
                "fr": "Salut! 👋",
                "de": "Hallo! 👋",
                "ja": "やあ! 👋"
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
                "fr": "BONJOUR!!! 🎉✨ Bienvenue dans le monde fantastique d'A2A!",
                "de": "HALLO!!! 🎉✨ Willkommen in der erstaunlichen Welt von A2A!",
                "ja": "HELLO THERE!!! 🎉✨ A2Aの素晴らしい世界へようこそ！"
            },
            "multilingual": {
                "en": "Hello • Hola • Bonjour • Hallo • こんにちは",
                "es": "Hello • Hola • Bonjour • Hallo • こんにちは", 
                "fr": "Hello • Hola • Bonjour • Hallo • こんにちは",
                "de": "Hello • Hola • Bonjour • Hallo • こんにちは",
                "ja": "Hello • Hola • Bonjour • Hallo • こんにちは"
            }
        }
        
        self._all_styles = list(self._greetings.keys())
        self._all_languages = list(self._greetings["casual"].keys())

    def handle_random_method(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the message/random JSON-RPC method."""
        try:
            # Validate required parameters
            if "id" not in params:
                raise ValueError("Missing required parameter: id")
            
            request_id = params["id"]
            exclude_styles = params.get("excludeStyles", [])
            exclude_languages = params.get("excludeLanguages", [])
            seed = params.get("seed")
            
            # Set random seed if provided for reproducible results
            if seed is not None:
                random.seed(seed)
            
            # Filter available options
            available_styles = [s for s in self._all_styles if s not in exclude_styles]
            available_languages = [l for l in self._all_languages if l not in exclude_languages]
            
            # Check if we have valid combinations
            if not available_styles or not available_languages:
                return self._create_error_response(-32001, "No valid style/language combinations available")
            
            # Select random style and language
            selected_style = random.choice(available_styles)
            selected_language = random.choice(available_languages)
            
            # Generate the greeting
            greeting_text = self._greetings[selected_style][selected_language]
            
            # Create message response
            message_id = f"msg-random-{uuid.uuid4().hex[:8]}"
            
            response = {
                "kind": "message",
                "messageId": message_id,
                "parts": [
                    {
                        "kind": "text",
                        "text": greeting_text
                    }
                ],
                "role": "agent",
                "metadata": {
                    "randomSelection": {
                        "style": selected_style,
                        "language": selected_language
                    }
                }
            }
            
            # Add seed to metadata if it was provided
            if seed is not None:
                response["metadata"]["randomSelection"]["seed"] = seed
            
            return response
            
        except ValueError as e:
            return self._create_error_response(-32602, f"Invalid params: {str(e)}")
        except Exception as e:
            return self._create_error_response(-32002, f"Random generation failed: {str(e)}")

    def _create_error_response(self, code: int, message: str) -> Dict[str, Any]:
        """Create a JSON-RPC error response."""
        return {
            "error": {
                "code": code,
                "message": message
            }
        }

    def get_extension_metadata(self) -> Dict[str, Any]:
        """Get extension metadata for agent card."""
        return {
            "uri": self.extension_uri,
            "name": "Random Greeting Method Extension",
            "version": "1.0.0",
            "type": "method",
            "methods": [self.method_name],
            "description": "Adds message/random method for generating random greetings"
        }