#!/usr/bin/env python3
"""
Simple HTTP server to host the Time-Based Greeting Extension specification.
This serves the extension documentation and specification at localhost:8080.
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

class ExtensionSpecHandler(BaseHTTPRequestHandler):
    """HTTP handler for serving extension specification and documentation."""
    
    def do_GET(self):
        """Handle GET requests for extension documentation."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/extensions/time-greeting/v1':
            # Serve the time greeting extension specification
            self.serve_extension_spec('time_greeting_extension_spec.json')
        elif path == '/extensions/time-greeting/v1/docs':
            # Serve time greeting documentation
            self.serve_time_greeting_documentation()
        elif path == '/extensions/time-greeting/v1/changelog':
            # Serve time greeting changelog
            self.serve_changelog()
        elif path == '/extensions/time-greeting/v1/schema':
            # Serve time greeting JSON schema
            self.serve_schema()
        elif path == '/':
            # Serve index page
            self.serve_index()
        else:
            self.send_error(404, f"Extension resource not found: {path}")

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-A2A-Extensions')
        self.end_headers()

    def send_cors_headers(self):
        """Send CORS headers for cross-origin requests."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-A2A-Extensions')

    def serve_extension_spec(self, filename):
        """Serve the extension specification JSON."""
        try:
            with open(filename, 'r') as f:
                spec = json.load(f)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(spec, indent=2).encode())
        except FileNotFoundError:
            self.send_error(500, f"Extension specification not found: {filename}")

    def serve_time_greeting_documentation(self):
        """Serve human-readable HTML documentation."""
        html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Time-Based Greeting Extension Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .code { background: #f8f8f8; padding: 10px; border-radius: 3px; font-family: monospace; }
        .example { border-left: 3px solid #007cba; padding-left: 15px; margin: 15px 0; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .time-period { background: #e8f4fd; padding: 10px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🕒 Time-Based Greeting Extension v1.0.0</h1>
        <p><strong>URI:</strong> <code>http://localhost:8080/extensions/time-greeting/v1</code></p>
        <p>A2A extension that provides contextually appropriate greetings based on current time of day.</p>
    </div>

    <div class="section">
        <h2>📋 Overview</h2>
        <p>This extension analyzes the current time and generates appropriate greetings based on time periods, with support for multiple timezones, languages, and greeting styles.</p>
    </div>

    <div class="section">
        <h2>🕐 Time Periods</h2>
        <div class="time-period">
            <strong>Dawn (5:00-6:59 AM):</strong> Early morning as the sun rises ☀️
        </div>
        <div class="time-period">
            <strong>Morning (7:00-11:59 AM):</strong> Standard morning hours ☀️
        </div>
        <div class="time-period">
            <strong>Noon (12:00-12:59 PM):</strong> Midday hour 🌞
        </div>
        <div class="time-period">
            <strong>Afternoon (1:00-5:59 PM):</strong> Afternoon hours 🌤️
        </div>
        <div class="time-period">
            <strong>Evening (6:00-8:59 PM):</strong> Early evening hours 🌅
        </div>
        <div class="time-period">
            <strong>Night (9:00-10:59 PM):</strong> Night hours 🌙
        </div>
        <div class="time-period">
            <strong>Late Night (11:00 PM-4:59 AM):</strong> Late night and very early morning 🌛
        </div>
    </div>

    <div class="section">
        <h2>🎨 Greeting Styles</h2>
        <table>
            <tr><th>Style</th><th>Description</th><th>Example</th></tr>
            <tr><td><code>casual</code></td><td>Friendly, conversational greetings</td><td>"Good morning! Hope you're having a great start to your day! ☀️"</td></tr>
            <tr><td><code>formal</code></td><td>Professional, courteous greetings</td><td>"Good morning. I trust you are having a productive morning."</td></tr>
            <tr><td><code>brief</code></td><td>Short, concise greetings</td><td>"Good morning! ☀️"</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>🌐 Supported Languages</h2>
        <ul>
            <li><code>en</code> - English</li>
            <li><code>es</code> - Spanish (Español)</li>
            <li><code>fr</code> - French (Français)</li>
            <li><code>de</code> - German (Deutsch)</li>
            <li><code>ja</code> - Japanese (日本語)</li>
        </ul>
    </div>

    <div class="section">
        <h2>🌍 Timezone Support</h2>
        <p>Supports major timezones including:</p>
        <ul>
            <li><code>UTC</code>, <code>GMT</code> - Universal time</li>
            <li><code>America/New_York</code>, <code>America/Los_Angeles</code> - US timezones</li>
            <li><code>Europe/London</code>, <code>Europe/Paris</code> - European timezones</li>
            <li><code>Asia/Tokyo</code>, <code>Asia/Shanghai</code> - Asian timezones</li>
            <li><code>local</code> - System local timezone (default)</li>
        </ul>
    </div>

    <div class="section">
        <h2>🔧 Activation</h2>
        <p>Activate this extension using keywords in your message:</p>
        <ul>
            <li><code>time greeting</code></li>
            <li><code>good morning</code> / <code>good afternoon</code> / <code>good evening</code></li>
            <li><code>what time is it</code></li>
            <li><code>current time greeting</code></li>
            <li><code>greet me based on time</code></li>
        </ul>
        
        <p>Or use the extension header:</p>
        <div class="code">X-A2A-Extensions: http://localhost:8080/extensions/time-greeting/v1</div>
    </div>

    <div class="section">
        <h2>💡 Example Usage</h2>
        <div class="example">
            <h3>Basic time greeting:</h3>
            <div class="code">curl -X POST http://localhost:9999/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "messageId": "msg-001",
        "parts": [{"kind": "text", "text": "time greeting"}],
        "role": "user"
      }
    }
  }'</div>
            <p><strong>Response:</strong> "Good afternoon! Hope your day is going well! 🌤️ It's currently 2:30 PM."</p>
        </div>
        
        <div class="example">
            <h3>Time greeting with timezone:</h3>
            <div class="code">Message: "time greeting in Tokyo"</div>
            <p><strong>Response:</strong> "Good evening! Time to start winding down! 🌅 It's currently 7:30 PM in Tokyo."</p>
        </div>
        
        <div class="example">
            <h3>Formal Spanish greeting:</h3>
            <div class="code">Message: "formal time greeting in Spanish"</div>
            <p><strong>Response:</strong> "Buenas tardes. Espero que tenga un día productivo. Son las 2:30 PM."</p>
        </div>
    </div>

    <div class="section">
        <h2>⚙️ Parameters</h2>
        <table>
            <tr><th>Parameter</th><th>Type</th><th>Default</th><th>Description</th></tr>
            <tr><td><code>timezone</code></td><td>string</td><td>"local"</td><td>Target timezone</td></tr>
            <tr><td><code>format</code></td><td>enum</td><td>"12h"</td><td>Time format ("12h" or "24h")</td></tr>
            <tr><td><code>includeTime</code></td><td>boolean</td><td>true</td><td>Include current time in response</td></tr>
            <tr><td><code>style</code></td><td>enum</td><td>"casual"</td><td>Greeting style</td></tr>
            <tr><td><code>language</code></td><td>enum</td><td>"en"</td><td>Response language</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>📚 Resources</h2>
        <ul>
            <li><a href="/extensions/time-greeting/v1">Extension Specification (JSON)</a></li>
            <li><a href="/extensions/time-greeting/v1/schema">JSON Schema</a></li>
            <li><a href="/extensions/time-greeting/v1/changelog">Changelog</a></li>
        </ul>
    </div>
</body>
</html>
        '''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(html_content.encode())

    def serve_changelog(self):
        """Serve the extension changelog."""
        changelog = {
            "version": "1.0.0",
            "date": "2024-08-26",
            "changes": [
                {
                    "type": "initial",
                    "description": "Initial release of Time-Based Greeting Extension",
                    "details": [
                        "Support for 7 time periods: dawn, morning, noon, afternoon, evening, night, late_night",
                        "Support for 5 languages: English, Spanish, French, German, Japanese",
                        "Support for 3 greeting styles: casual, formal, brief",
                        "Timezone support with major world timezones",
                        "Natural language parameter parsing",
                        "A2A protocol compliance with proper extension metadata",
                        "Comprehensive documentation and examples"
                    ]
                }
            ]
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(changelog, indent=2).encode())

    def serve_schema(self):
        """Serve JSON schema for extension parameters validation."""
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "Time-Based Greeting Extension Parameters",
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Unique identifier for the request"
                },
                "timezone": {
                    "type": "string",
                    "default": "local",
                    "description": "Target timezone (e.g., 'UTC', 'America/New_York', 'Asia/Tokyo')",
                    "examples": ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]
                },
                "format": {
                    "type": "string",
                    "enum": ["12h", "24h"],
                    "default": "12h",
                    "description": "Time format preference"
                },
                "includeTime": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to include current time in the response"
                },
                "style": {
                    "type": "string",
                    "enum": ["casual", "formal", "brief"],
                    "default": "casual",
                    "description": "Greeting style preference"
                },
                "language": {
                    "type": "string",
                    "enum": ["en", "es", "fr", "de", "ja"],
                    "default": "en",
                    "description": "Language for the greeting"
                }
            },
            "required": ["id"],
            "additionalProperties": False,
            "examples": [
                {"id": "test-1", "timezone": "UTC", "style": "formal"},
                {"id": "test-2", "language": "es", "format": "24h"},
                {"id": "test-3", "timezone": "Asia/Tokyo", "style": "brief", "includeTime": False}
            ]
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(schema, indent=2).encode())

    def serve_index(self):
        """Serve a simple index page."""
        html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>A2A Extension Server</title>
    <style>body { font-family: Arial, sans-serif; margin: 40px; }</style>
</head>
<body>
    <h1>🚀 A2A Extension Server</h1>
    <p>This server hosts A2A protocol extensions for demonstration purposes.</p>
    <h2>Available Extensions:</h2>
    <ul>
        <li><a href="/extensions/time-greeting/v1">Time-Based Greeting Extension v1.0.0</a> - <a href="/extensions/time-greeting/v1/docs">📚 Documentation</a></li>
    </ul>
</body>
</html>
        '''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(html_content.encode())

    def log_message(self, format, *args):
        """Override to customize log format."""
        print(f"[Extension Server] {self.address_string()} - {format % args}")


def start_extension_server(port=8080):
    """Start the extension specification server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, ExtensionSpecHandler)
    
    print(f"🚀 Extension Server starting on http://localhost:{port}")
    print(f"📚 Time Greeting Documentation: http://localhost:{port}/extensions/time-greeting/v1/docs")
    print(f"📋 Time Greeting Specification: http://localhost:{port}/extensions/time-greeting/v1")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\n🛑 Extension Server stopped")
        httpd.server_close()


if __name__ == '__main__':
    start_extension_server()