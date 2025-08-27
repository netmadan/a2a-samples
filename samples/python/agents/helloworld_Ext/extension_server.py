#!/usr/bin/env python3
"""
Simple HTTP server to host the Greeting Style Extension specification.
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
        
        if path == '/extensions/greeting-style/v1':
            # Serve the greeting style extension specification
            self.serve_extension_spec('extension_spec.json')
        elif path == '/extensions/greeting-style/v1/docs':
            # Serve greeting style documentation
            self.serve_greeting_style_documentation()
        elif path == '/extensions/greeting-style/v1/changelog':
            # Serve greeting style changelog
            self.serve_changelog('greeting-style')
        elif path == '/extensions/greeting-style/v1/schema':
            # Serve greeting style JSON schema
            self.serve_schema('greeting-style')
        elif path == '/extensions/random-greeting-method/v1':
            # Serve the random method extension specification
            self.serve_extension_spec('random_method_extension_spec.json')
        elif path == '/extensions/random-greeting-method/v1/docs':
            # Serve random method documentation
            self.serve_random_method_documentation()
        elif path == '/extensions/random-greeting-method/v1/changelog':
            # Serve random method changelog
            self.serve_changelog('random-method')
        elif path == '/extensions/random-greeting-method/v1/schema':
            # Serve random method JSON schema
            self.serve_schema('random-method')
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

    def serve_greeting_style_documentation(self):
        """Serve human-readable HTML documentation."""
        html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Greeting Style Extension Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .code { background: #f8f8f8; padding: 10px; border-radius: 3px; font-family: monospace; }
        .example { border-left: 3px solid #007cba; padding-left: 15px; margin: 15px 0; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 Greeting Style Extension v1.0.0</h1>
        <p><strong>URI:</strong> <code>http://localhost:8080/extensions/greeting-style/v1</code></p>
        <p>A2A extension for customizing greeting styles and languages in agent responses.</p>
    </div>

    <div class="section">
        <h2>📋 Overview</h2>
        <p>This extension allows A2A agents to provide customized greetings in multiple styles and languages. It supports both data extension (metadata in agent card) and profile extension (message constraints) patterns.</p>
    </div>

    <div class="section">
        <h2>🎨 Supported Styles</h2>
        <table>
            <tr><th>Style</th><th>Description</th><th>Example</th></tr>
            <tr><td><code>casual</code></td><td>Friendly, informal greetings</td><td>"Hey there! 👋"</td></tr>
            <tr><td><code>formal</code></td><td>Professional, courteous greetings</td><td>"Good day. I am pleased to make your acquaintance."</td></tr>
            <tr><td><code>enthusiastic</code></td><td>Energetic, exciting greetings with emojis</td><td>"HELLO THERE!!! 🎉✨"</td></tr>
            <tr><td><code>multilingual</code></td><td>Greetings in multiple languages</td><td>"Hello • Hola • Bonjour • Hallo • こんにちは"</td></tr>
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
        <h2>🔧 Activation</h2>
        <p>Activate this extension by including the extension URI in the request header:</p>
        <div class="code">X-A2A-Extensions: http://localhost:8080/extensions/greeting-style/v1</div>
        
        <p>Pass parameters via message metadata:</p>
        <div class="code">{
  "metadata": {
    "extensions": {
      "http://localhost:8080/extensions/greeting-style/v1": {
        "style": "formal",
        "language": "fr"
      }
    }
  }
}</div>
    </div>

    <div class="section">
        <h2>💡 Example Usage</h2>
        <div class="example">
            <h3>Request formal French greeting:</h3>
            <div class="code">curl -X POST http://localhost:9999/ \\
  -H "Content-Type: application/json" \\
  -H "X-A2A-Extensions: http://localhost:8080/extensions/greeting-style/v1" \\
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "metadata": {
          "extensions": {
            "http://localhost:8080/extensions/greeting-style/v1": {
              "style": "formal",
              "language": "fr"
            }
          }
        }
      }
    }
  }'</div>
            <p><strong>Response:</strong> "Bonjour. Je suis ravi de faire votre connaissance."</p>
        </div>
    </div>

    <div class="section">
        <h2>📚 Resources</h2>
        <ul>
            <li><a href="/extensions/greeting-style/v1">Extension Specification (JSON)</a></li>
            <li><a href="/extensions/greeting-style/v1/schema">JSON Schema</a></li>
            <li><a href="/extensions/greeting-style/v1/changelog">Changelog</a></li>
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

    def serve_changelog(self, extension_type):
        """Serve the extension changelog."""
        if extension_type == 'greeting-style':
            changelog = {
                "version": "1.0.0",
                "date": "2024-08-26",
                "changes": [
                    {
                        "type": "initial",
                        "description": "Initial release of Greeting Style Extension",
                        "details": [
                            "Support for 4 greeting styles: casual, formal, enthusiastic, multilingual",
                            "Support for 5 languages: English, Spanish, French, German, Japanese",
                            "Data extension for agent card metadata",
                            "Profile extension for message parameter validation",
                            "Comprehensive documentation and examples"
                        ]
                    }
                ]
            }
        else:  # random-method
            changelog = {
                "version": "1.0.0",
                "date": "2024-08-26",
                "changes": [
                    {
                        "type": "initial",
                        "description": "Initial release of Random Greeting Method Extension",
                        "details": [
                            "Added message/random JSON-RPC method",
                            "Support for random style and language selection",
                            "Exclusion filters for styles and languages",
                            "Reproducible results with optional seed parameter",
                            "Complete A2A method extension implementation"
                        ]
                    }
                ]
            }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(changelog, indent=2).encode())

    def serve_schema(self, extension_type):
        """Serve JSON schema for extension parameters validation."""
        if extension_type == 'greeting-style':
            schema = {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "title": "Greeting Style Extension Parameters",
                "type": "object",
                "properties": {
                    "style": {
                        "type": "string",
                        "enum": ["casual", "formal", "enthusiastic", "multilingual"],
                        "default": "casual",
                        "description": "The greeting style to use"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["en", "es", "fr", "de", "ja"],
                        "default": "en",
                        "description": "The language code for the greeting"
                    }
                },
                "additionalProperties": False,
                "examples": [
                    {"style": "casual", "language": "en"},
                    {"style": "formal", "language": "fr"},
                    {"style": "enthusiastic", "language": "ja"}
                ]
            }
        else:  # random-method
            schema = {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "title": "Random Greeting Method Parameters",
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Unique identifier for the request"
                    },
                    "excludeStyles": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["casual", "formal", "enthusiastic", "multilingual"]},
                        "description": "List of styles to exclude from random selection"
                    },
                    "excludeLanguages": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["en", "es", "fr", "de", "ja"]},
                        "description": "List of languages to exclude from random selection"
                    },
                    "seed": {
                        "type": "integer",
                        "minimum": 0,
                        "description": "Optional random seed for reproducible results"
                    }
                },
                "required": ["id"],
                "additionalProperties": False
            }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(schema, indent=2).encode())

    def serve_random_method_documentation(self):
        """Serve human-readable HTML documentation for the random method extension."""
        html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Random Greeting Method Extension Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .code { background: #f8f8f8; padding: 10px; border-radius: 3px; font-family: monospace; }
        .example { border-left: 3px solid #007cba; padding-left: 15px; margin: 15px 0; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎲 Random Greeting Method Extension v1.0.0</h1>
        <p><strong>URI:</strong> <code>http://localhost:8080/extensions/random-greeting-method/v1</code></p>
        <p>A2A method extension that adds a new JSON-RPC method for generating random greetings.</p>
    </div>

    <div class="section">
        <h2>📋 Overview</h2>
        <p>This extension adds a new <code>message/random</code> method to the A2A protocol. This method generates random greetings by randomly selecting a style and language combination from the available options.</p>
    </div>

    <div class="section">
        <h2>🔧 Method Specification</h2>
        <p><strong>Method Name:</strong> <code>message/random</code></p>
        <p><strong>Description:</strong> Generate a random greeting with random style and language combination</p>
        
        <h3>Parameters</h3>
        <table>
            <tr><th>Parameter</th><th>Type</th><th>Required</th><th>Description</th></tr>
            <tr><td><code>id</code></td><td>string</td><td>Yes</td><td>Unique identifier for the request</td></tr>
            <tr><td><code>excludeStyles</code></td><td>array</td><td>No</td><td>List of styles to exclude from random selection</td></tr>
            <tr><td><code>excludeLanguages</code></td><td>array</td><td>No</td><td>List of languages to exclude from random selection</td></tr>
            <tr><td><code>seed</code></td><td>integer</td><td>No</td><td>Optional random seed for reproducible results</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>💡 Example Usage</h2>
        <div class="example">
            <h3>Basic random greeting request:</h3>
            <div class="code">curl -X POST http://localhost:9999/ \\
  -H "Content-Type: application/json" \\
  -H "X-A2A-Extensions: http://localhost:8080/extensions/random-greeting-method/v1" \\
  -d '{
    "jsonrpc": "2.0",
    "id": "random-test-1",
    "method": "message/random",
    "params": {
      "id": "task-random-1"
    }
  }'</div>
        </div>
        
        <div class="example">
            <h3>Random greeting with exclusions:</h3>
            <div class="code">{
  "jsonrpc": "2.0",
  "id": "random-test-2",
  "method": "message/random",
  "params": {
    "id": "task-random-2",
    "excludeStyles": ["enthusiastic"],
    "excludeLanguages": ["ja", "de"]
  }
}</div>
        </div>
    </div>

    <div class="section">
        <h2>📚 Resources</h2>
        <ul>
            <li><a href="/extensions/random-greeting-method/v1">Extension Specification (JSON)</a></li>
            <li><a href="/extensions/random-greeting-method/v1/schema">JSON Schema</a></li>
            <li><a href="/extensions/random-greeting-method/v1/changelog">Changelog</a></li>
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
        <li><a href="/extensions/greeting-style/v1">Greeting Style Extension v1.0.0</a> - <a href="/extensions/greeting-style/v1/docs">📚 Documentation</a></li>
        <li><a href="/extensions/random-greeting-method/v1">Random Greeting Method Extension v1.0.0</a> - <a href="/extensions/random-greeting-method/v1/docs">📚 Documentation</a></li>
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
    print(f"📚 Greeting Style Documentation: http://localhost:{port}/extensions/greeting-style/v1/docs")
    print(f"📋 Greeting Style Specification: http://localhost:{port}/extensions/greeting-style/v1")
    print(f"📚 Random Method Documentation: http://localhost:{port}/extensions/random-greeting-method/v1/docs")
    print(f"📋 Random Method Specification: http://localhost:{port}/extensions/random-greeting-method/v1")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\n🛑 Extension Server stopped")
        httpd.server_close()


if __name__ == '__main__':
    start_extension_server()