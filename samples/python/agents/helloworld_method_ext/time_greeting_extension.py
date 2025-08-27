#!/usr/bin/env python3
"""
Time-Based Greeting Extension for A2A Protocol.
Provides contextually appropriate greetings based on current time of day.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any
try:
    import zoneinfo  # Python 3.9+
except ImportError:
    try:
        import pytz as zoneinfo  # Fallback for older Python
    except ImportError:
        zoneinfo = None


class TimeGreetingExtension:
    """Implementation of the time-based greeting extension."""
    
    def __init__(self):
        self.extension_uri = "http://localhost:8080/extensions/time-greeting/v1"
        self.method_name = "greeting/time-based"
        
        # Greeting templates organized by time period, language, and style
        self._greetings = {
            "dawn": {
                "en": {
                    "casual": "Good early morning! The sun is just rising. ☀️",
                    "formal": "Good morning. The day is beginning early.",
                    "brief": "Early morning! ☀️"
                },
                "es": {
                    "casual": "¡Buenos días temprano! El sol está saliendo. ☀️",
                    "formal": "Buenos días. El día está comenzando temprano.",
                    "brief": "¡Madrugada! ☀️"
                },
                "fr": {
                    "casual": "Bon petit matin! Le soleil se lève. ☀️",
                    "formal": "Bonjour. La journée commence tôt.",
                    "brief": "Petit matin! ☀️"
                },
                "de": {
                    "casual": "Guten frühen Morgen! Die Sonne geht auf. ☀️",
                    "formal": "Guten Morgen. Der Tag beginnt früh.",
                    "brief": "Früher Morgen! ☀️"
                },
                "ja": {
                    "casual": "おはようございます！太陽が昇っています。☀️",
                    "formal": "おはようございます。一日が早く始まります。",
                    "brief": "早朝！☀️"
                }
            },
            "morning": {
                "en": {
                    "casual": "Good morning! Hope you're having a great start to your day! ☀️",
                    "formal": "Good morning. I trust you are having a productive morning.",
                    "brief": "Good morning! ☀️"
                },
                "es": {
                    "casual": "¡Buenos días! ¡Espero que tengas un gran comienzo de día! ☀️",
                    "formal": "Buenos días. Espero que tenga una mañana productiva.",
                    "brief": "¡Buenos días! ☀️"
                },
                "fr": {
                    "casual": "Bonjour! J'espère que vous passez un bon début de journée! ☀️",
                    "formal": "Bonjour. J'espère que vous passez une matinée productive.",
                    "brief": "Bonjour! ☀️"
                },
                "de": {
                    "casual": "Guten Morgen! Ich hoffe, Sie haben einen guten Start in den Tag! ☀️",
                    "formal": "Guten Morgen. Ich hoffe, Sie haben einen produktiven Morgen.",
                    "brief": "Guten Morgen! ☀️"
                },
                "ja": {
                    "casual": "おはようございます！素晴らしい一日の始まりを！☀️",
                    "formal": "おはようございます。生産的な朝をお過ごしください。",
                    "brief": "おはよう！☀️"
                }
            },
            "noon": {
                "en": {
                    "casual": "Good afternoon! Perfect time for lunch! 🌞",
                    "formal": "Good afternoon. I hope your midday is going well.",
                    "brief": "Good afternoon! 🌞"
                },
                "es": {
                    "casual": "¡Buenas tardes! ¡Momento perfecto para almorzar! 🌞",
                    "formal": "Buenas tardes. Espero que su mediodía vaya bien.",
                    "brief": "¡Buenas tardes! 🌞"
                },
                "fr": {
                    "casual": "Bon après-midi! Parfait pour le déjeuner! 🌞",
                    "formal": "Bon après-midi. J'espère que votre midi se passe bien.",
                    "brief": "Bon après-midi! 🌞"
                },
                "de": {
                    "casual": "Guten Tag! Perfekte Zeit fürs Mittagessen! 🌞",
                    "formal": "Guten Tag. Ich hoffe, Ihr Mittag verläuft gut.",
                    "brief": "Guten Tag! 🌞"
                },
                "ja": {
                    "casual": "こんにちは！昼食に最適な時間ですね！🌞",
                    "formal": "こんにちは。お昼がうまくいっていることを願います。",
                    "brief": "こんにちは！🌞"
                }
            },
            "afternoon": {
                "en": {
                    "casual": "Good afternoon! Hope your day is going well! 🌤️",
                    "formal": "Good afternoon. I trust you are having a productive day.",
                    "brief": "Good afternoon! 🌤️"
                },
                "es": {
                    "casual": "¡Buenas tardes! ¡Espero que tu día vaya bien! 🌤️",
                    "formal": "Buenas tardes. Espero que tenga un día productivo.",
                    "brief": "¡Buenas tardes! 🌤️"
                },
                "fr": {
                    "casual": "Bon après-midi! J'espère que votre journée se passe bien! 🌤️",
                    "formal": "Bon après-midi. J'espère que vous passez une journée productive.",
                    "brief": "Bon après-midi! 🌤️"
                },
                "de": {
                    "casual": "Guten Tag! Ich hoffe, Ihr Tag verläuft gut! 🌤️",
                    "formal": "Guten Tag. Ich hoffe, Sie haben einen produktiven Tag.",
                    "brief": "Guten Tag! 🌤️"
                },
                "ja": {
                    "casual": "こんにちは！良い一日をお過ごしください！🌤️",
                    "formal": "こんにちは。生産的な一日をお過ごしください。",
                    "brief": "こんにちは！🌤️"
                }
            },
            "evening": {
                "en": {
                    "casual": "Good evening! Time to start winding down! 🌅",
                    "formal": "Good evening. I hope you are having a pleasant evening.",
                    "brief": "Good evening! 🌅"
                },
                "es": {
                    "casual": "¡Buenas noches! ¡Hora de comenzar a relajarse! 🌅",
                    "formal": "Buenas noches. Espero que tenga una tarde agradable.",
                    "brief": "¡Buenas noches! 🌅"
                },
                "fr": {
                    "casual": "Bonsoir! Il est temps de commencer à se détendre! 🌅",
                    "formal": "Bonsoir. J'espère que vous passez une soirée agréable.",
                    "brief": "Bonsoir! 🌅"
                },
                "de": {
                    "casual": "Guten Abend! Zeit, sich zu entspannen! 🌅",
                    "formal": "Guten Abend. Ich hoffe, Sie haben einen angenehmen Abend.",
                    "brief": "Guten Abend! 🌅"
                },
                "ja": {
                    "casual": "こんばんは！リラックスする時間ですね！🌅",
                    "formal": "こんばんは。素敵な夜をお過ごしください。",
                    "brief": "こんばんは！🌅"
                }
            },
            "night": {
                "en": {
                    "casual": "Good evening! Getting late, but still time to relax! 🌙",
                    "formal": "Good evening. The day is drawing to a close.",
                    "brief": "Good evening! 🌙"
                },
                "es": {
                    "casual": "¡Buenas noches! Se está haciendo tarde, ¡pero aún hay tiempo para relajarse! 🌙",
                    "formal": "Buenas noches. El día está llegando a su fin.",
                    "brief": "¡Buenas noches! 🌙"
                },
                "fr": {
                    "casual": "Bonsoir! Il se fait tard, mais il y a encore du temps pour se détendre! 🌙",
                    "formal": "Bonsoir. La journée touche à sa fin.",
                    "brief": "Bonsoir! 🌙"
                },
                "de": {
                    "casual": "Guten Abend! Es wird spät, aber es ist noch Zeit zum Entspannen! 🌙",
                    "formal": "Guten Abend. Der Tag neigt sich dem Ende zu.",
                    "brief": "Guten Abend! 🌙"
                },
                "ja": {
                    "casual": "こんばんは！遅くなりましたが、まだリラックスする時間があります！🌙",
                    "formal": "こんばんは。一日が終わりに近づいています。",
                    "brief": "こんばんは！🌙"
                }
            },
            "late_night": {
                "en": {
                    "casual": "Good night! You're up quite late! 🌛",
                    "formal": "Good evening. You are up rather late tonight.",
                    "brief": "Late night! 🌛"
                },
                "es": {
                    "casual": "¡Buenas noches! ¡Estás despierto bastante tarde! 🌛",
                    "formal": "Buenas noches. Está despierto bastante tarde esta noche.",
                    "brief": "¡Noche tardía! 🌛"
                },
                "fr": {
                    "casual": "Bonne nuit! Vous êtes debout assez tard! 🌛",
                    "formal": "Bonsoir. Vous êtes debout assez tard ce soir.",
                    "brief": "Nuit tardive! 🌛"
                },
                "de": {
                    "casual": "Gute Nacht! Sie sind ziemlich spät auf! 🌛",
                    "formal": "Guten Abend. Sie sind heute Abend ziemlich spät wach.",
                    "brief": "Späte Nacht! 🌛"
                },
                "ja": {
                    "casual": "こんばんは！かなり遅くまで起きていますね！🌛",
                    "formal": "こんばんは。今夜は遅くまで起きていらっしゃいますね。",
                    "brief": "深夜！🌛"
                }
            }
        }
        
        self._supported_timezones = {
            "UTC", "local", "GMT",
            "America/New_York", "America/Los_Angeles", "America/Chicago", "America/Denver",
            "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Rome",
            "Asia/Tokyo", "Asia/Shanghai", "Asia/Mumbai", "Asia/Dubai",
            "Australia/Sydney", "Pacific/Auckland"
        }

    def get_time_period(self, hour: int) -> str:
        """Determine time period based on hour (0-23)."""
        if 5 <= hour < 7:
            return "dawn"
        elif 7 <= hour < 12:
            return "morning"
        elif hour == 12:
            return "noon"
        elif 13 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 21:
            return "evening"
        elif 21 <= hour < 23:
            return "night"
        else:  # 23, 0, 1, 2, 3, 4
            return "late_night"

    def get_current_time_info(self, timezone_str: str = "local") -> Dict[str, Any]:
        """Get current time information for the specified timezone."""
        try:
            if timezone_str == "local":
                current_time = datetime.now()
                tz_name = "local"
            else:
                if zoneinfo and hasattr(zoneinfo, 'ZoneInfo'):
                    # Python 3.9+ zoneinfo
                    tz = zoneinfo.ZoneInfo(timezone_str)
                    current_time = datetime.now(tz)
                elif hasattr(zoneinfo, 'timezone'):
                    # pytz fallback
                    tz = zoneinfo.timezone(timezone_str)
                    current_time = datetime.now(tz)
                else:
                    # No timezone support, fall back to local time
                    current_time = datetime.now()
                    timezone_str = "local (timezone support unavailable)"
                
                tz_name = timezone_str
            
            return {
                "datetime": current_time,
                "timezone": tz_name,
                "hour": current_time.hour,
                "time_period": self.get_time_period(current_time.hour)
            }
        except Exception as e:
            # Fall back to local time if timezone is invalid
            current_time = datetime.now()
            return {
                "datetime": current_time,
                "timezone": "local (fallback)",
                "hour": current_time.hour,
                "time_period": self.get_time_period(current_time.hour),
                "error": f"Invalid timezone '{timezone_str}', using local time"
            }

    def format_time(self, dt: datetime, format_type: str = "12h") -> str:
        """Format time according to specified format."""
        if format_type == "24h":
            return dt.strftime("%H:%M")
        else:  # 12h format
            return dt.strftime("%I:%M %p").lstrip('0')

    def get_greeting(self, time_period: str, language: str = "en", style: str = "casual") -> str:
        """Get greeting text for specified parameters."""
        try:
            return self._greetings[time_period][language][style]
        except KeyError:
            # Fallback to English casual if specific combination not found
            return self._greetings.get(time_period, {}).get("en", {}).get("casual", "Hello!")

    def handle_time_greeting_method(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the time-based greeting method."""
        try:
            # Validate required parameters
            if "id" not in params:
                raise ValueError("Missing required parameter: id")
            
            request_id = params["id"]
            timezone_str = params.get("timezone", "local")
            format_type = params.get("format", "12h")
            include_time = params.get("includeTime", True)
            style = params.get("style", "casual")
            language = params.get("language", "en")
            
            # Validate parameters
            if language not in ["en", "es", "fr", "de", "ja"]:
                return self._create_error_response(-32003, f"Unsupported language: {language}")
            
            if style not in ["casual", "formal", "brief"]:
                style = "casual"  # Default fallback
            
            if format_type not in ["12h", "24h"]:
                format_type = "12h"  # Default fallback
                
            # Get current time information
            time_info = self.get_current_time_info(timezone_str)
            
            if "error" in time_info and timezone_str not in ["local", "local (fallback)"]:
                return self._create_error_response(-32001, f"Invalid timezone: {timezone_str}")
            
            # Generate greeting
            greeting_text = self.get_greeting(time_info["time_period"], language, style)
            
            # Add time information if requested
            if include_time:
                formatted_time = self.format_time(time_info["datetime"], format_type)
                if time_info["timezone"] == "local":
                    time_suffix = f" It's currently {formatted_time}."
                else:
                    time_suffix = f" It's currently {formatted_time} in {time_info['timezone'].split('/')[-1] if '/' in time_info['timezone'] else time_info['timezone']}."
                greeting_text += time_suffix
            
            # Create message response
            message_id = f"msg-time-greeting-{uuid.uuid4().hex[:8]}"
            
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
                    "timeContext": {
                        "currentTime": self.format_time(time_info["datetime"], format_type),
                        "timezone": time_info["timezone"],
                        "timePeriod": time_info["time_period"],
                        "hour": time_info["hour"],
                        "style": style,
                        "language": language
                    }
                }
            }
            
            return response
            
        except ValueError as e:
            return self._create_error_response(-32602, f"Invalid params: {str(e)}")
        except Exception as e:
            return self._create_error_response(-32002, f"Time calculation failed: {str(e)}")

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
            "name": "Time-Based Greeting Extension",
            "version": "1.0.0",
            "type": "method",
            "methods": [self.method_name],
            "description": "Provides contextually appropriate greetings based on current time of day",
            "supportedTimezones": list(self._supported_timezones),
            "supportedLanguages": ["en", "es", "fr", "de", "ja"],
            "supportedStyles": ["casual", "formal", "brief"],
            "timePeriods": ["dawn", "morning", "noon", "afternoon", "evening", "night", "late_night"]
        }