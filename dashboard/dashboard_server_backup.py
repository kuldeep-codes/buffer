import os
import json
import http.server
import socketserver
import importlib
import threading
import time

# Default configuration
DEFAULT_CONFIG = {
    "server": {
        "host": "localhost",
        "port": 8000
    },
    "grid": {
        "columns": 3,
        "cellMinWidth": 400,
        "cellMinHeight": 300
    },
    "modules": {}
}

class DashboardServer:
    """
    Main server class for the modular dashboard
    """
    def __init__(self, config_path="config.json"):
        # Load configuration
        self.config = self.load_config(config_path)
        self.modules = {}
        self.load_modules()
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    print(f"Loaded configuration from {config_path}")
                    
                    # Ensure grid configuration exists
                    if "grid" not in config:
                        config["grid"] = {
                            "columns": 3,
                            "cellMinWidth": 400,
                            "cellMinHeight": 300
                        }
                        
                    return config
            except Exception as e:
                print(f"Error loading configuration: {e}")
        
        print(f"Configuration file not found or invalid. Using default configuration.")
        return DEFAULT_CONFIG
        
    def load_modules(self):
        """Load and initialize enabled modules"""
        for module_name, module_config in self.config["modules"].items():
            if module_config.get("enabled", False):
                try:
                    # Import the module dynamically
                    module_path = f"modules.{module_name}"
                    module = importlib.import_module(module_path)
                    
                    # Get the class name by capitalizing the module name and adding "Module"
                    class_name = module_name.capitalize() + "Module"
                    module_class = getattr(module, class_name)
                    
                    # Initialize the module with its configuration
                    module_instance = module_class(module_config["config"])
                    
                    # Add grid positioning information
                    if "grid" in module_config:
                        module_instance.grid = module_config["grid"]
                    else:
                        # Default grid position if not specified
                        module_instance.grid = {
                            "row": 0,
                            "column": len(self.modules),
                            "width": 400,
                            "height": 300
                        }
                    
                    self.modules[module_name] = module_instance
                    print(f"Loaded module: {module_name}")
                except Exception as e:
                    print(f"Error loading module {module_name}: {e}")
    
    def start(self):
        """Start the dashboard server"""
        host = self.config["server"]["host"]
        port = self.config["server"]["port"]
        
        # Create the request handler
        handler = self.create_request_handler()
        
        # Start the server
        with socketserver.TCPServer((host, port), handler) as httpd:
            print(f"Dashboard server started at http://{host}:{port}")
            print("Press Ctrl+C to stop the server.")
            httpd.serve_forever()
    
    def create_request_handler(self):
        """Create the HTTP request handler class"""
        modules = self.modules
        server = self
        
        class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                # Serve the main dashboard page
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    # Generate the dashboard HTML
                    html = self.generate_dashboard_html()
                    self.wfile.write(html.encode('utf-8'))
                    return
                
                # Handle API requests
                if self.path.startswith('/api/'):
                    for module_name, module in modules.items():
                        for route in module.get_api_routes():
                            if self.path == route["path"] and route["method"] == "GET":
                                self.send_response(200)
                                self.send_header('Content-type', 'application/json')
                                self.end_headers()
                                response = route["handler"]()
                                self.wfile.write(response.encode('utf-8'))
                                return
                
                # Fallback to the default handler for other paths (e.g., static files)
                return http.server.SimpleHTTPRequestHandler.do_GET(self)
                
            def generate_dashboard_html(self):
                # Get grid configuration
                grid_config = server.config.get("grid", {"columns": 3, "cellMinWidth": 400, "cellMinHeight": 300})
                columns = grid_config.get("columns", 3)
                cell_min_width = grid_config.get("cellMinWidth", 400)
                cell_min_height = grid_config.get("cellMinHeight", 300)
                
                # Organize widgets by grid position
                grid_layout = {}
                
                for module_name, module in modules.items():
                    grid_info = getattr(module, "grid", {
                        "row": 0,
                        "column": 0,
                        "width": cell_min_width,
                        "height": cell_min_height
                    })
                    
                    row = grid_info.get("row", 0)
                    column = grid_info.get("column", 0)
                    
                    # Ensure we stay within column bounds
                    column = min(column, columns - 1)
                    
                    # Create position key
                    pos_key = f"{row}:{column}"
                    
                    if pos_key not in grid_layout:
                        grid_layout[pos_key] = {
                            "modules": [],
                            "row": row,
                            "column": column
                        }
                    
                    grid_layout[pos_key]["modules"].append({
                        "name": module_name,
                        "module": module,
                        "width": grid_info.get("width", cell_min_width),
                        "height": grid_info.get("height", cell_min_height)
                    })
                
                # Build grid HTML
                widget_html = ""
                widget_js = ""
                
                # Find the maximum row
                max_row = 0
                if grid_layout:
                    max_row = max(int(pos.split(":")[0]) for pos in grid_layout.keys())
                
                # Generate HTML for each row
                for row in range(max_row + 1):
                    widget_html += f'<div class="dashboard-row" id="dashboard-row-{row}">\n'
                    
                    # Add cells for this row
                    for col in range(columns):
                        pos_key = f"{row}:{col}"
                        
                        if pos_key in grid_layout:
                            cell_modules = grid_layout[pos_key]["modules"]
                            
                            for module_data in cell_modules:
                                module = module_data["module"]
                                module_width = module_data["width"]
                                module_height = module_data["height"]
                                
                                # Add the module's HTML with specific width and height
                                widget_html += f'<div class="dashboard-cell" style="width: {module_width}px; height: {module_height}px">\n'
                                widget_html += module.get_widget_html()
                                widget_html += '</div>\n'
                                
                                # Add module's JavaScript
                                widget_js += module.get_widget_js()
                    
                    widget_html += '</div>\n'
                
                # Generate the complete HTML document
                html = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Modular Dashboard</title>
                    <style>
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            margin: 0;
                            padding: 20px;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            min-height: 100vh;
                        }}

                        .dashboard-row {{
                            display: flex;
                            flex-wrap: wrap;
                            gap: 20px;
                            margin-bottom: 20px;
                            justify-content: flex-start;
                        }}

                        .dashboard-cell {{
                            flex: 0 0 auto;
                            min-width: {cell_min_width}px;
                            margin-bottom: 20px;
                            display: flex;
                            flex-direction: column;
                        }}

                        .widget {{
                            background: rgba(255, 255, 255, 0.95);
                            border-radius: 20px;
                            padding: 30px;
                            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                            backdrop-filter: blur(10px);
                            height: 100%;
                            overflow: auto;
                            flex: 1;
                            display: flex;
                            flex-direction: column;
                        }}

                        .widget-title {{
                            color: #333;
                            margin-bottom: 20px;
                            font-size: 1.8em;
                            font-weight: 300;
                        }}
                        
                        /* Timesheet Widget Styles */
                        .time-display {{
                            font-size: 4em;
                            font-weight: bold;
                            color: #667eea;
                            margin: 30px 0;
                            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
                            font-family: 'Courier New', monospace;
                        }}

                        .status {{
                            font-size: 1.2em;
                            margin: 20px 0;
                            padding: 15px;
                            border-radius: 10px;
                            font-weight: 500;
                        }}

                        .status.active {{
                            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                            color: white;
                        }}

                        .status.inactive {{
                            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                            color: white;
                        }}

                        .status.error {{
                            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                            color: white;
                        }}

                        .status.loading {{
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                        }}

                        .last-updated {{
                            color: #666;
                            font-size: 0.9em;
                            margin-top: 20px;
                        }}

                        .loading {{
                            color: #667eea;
                            font-size: 1.1em;
                        }}

                        .pulse {{
                            animation: pulse 2s infinite;
                        }}

                        @keyframes pulse {{
                            0% {{ opacity: 1; }}
                            50% {{ opacity: 0.7; }}
                            100% {{ opacity: 1; }}
                        }}

                        .details {{
                            margin-top: 20px;
                            padding: 15px;
                            background: rgba(102, 126, 234, 0.1);
                            border-radius: 10px;
                            font-size: 0.9em;
                            color: #555;
                        }}
                        
                        /* Clusters Widget Styles */
                        table {{
                            border-collapse: collapse;
                            width: 100%;
                            margin-top: 1em;
                        }}
                        
                        th, td {{
                            border: 1px solid #dddddd;
                            text-align: left;
                            padding: 12px;
                        }}
                        
                        th {{
                            background-color: #667eea;
                            color: white;
                        }}
                        
                        progress {{
                            width: 100%;
                            height: 25px;
                            border-radius: 5px;
                        }}
                        
                        progress::-webkit-progress-bar {{
                            background-color: #eee;
                            border-radius: 5px;
                        }}
                        
                        progress::-webkit-progress-value {{
                            background-color: #28a745;
                            border-radius: 5px;
                            transition: width 0.4s ease;
                        }}
                        
                        progress::-moz-progress-bar {{
                            background-color: #28a745;
                            border-radius: 5px;
                            transition: width 0.4s ease;
                        }}
                    </style>
                </head>
                <body>
                    {widget_html}
                    
                    <script>
                        // Array to store initialization functions
                        const DASHBOARD_INIT_FUNCTIONS = [];
                        
                        {widget_js}
                        
                        // Initialize all widgets when the page loads
                        document.addEventListener('DOMContentLoaded', () => {{
                            DASHBOARD_INIT_FUNCTIONS.forEach(initFn => initFn());
                        }});
                    </script>
                </body>
                </html>
                """
                
                return html
                
        return DashboardRequestHandler

def main():
    """Main entry point"""
    try:
        # Create and start the dashboard server
        server = DashboardServer()
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down the server...")
        # Stop any background threads or resources
        for module_name, module in server.modules.items():
            if hasattr(module, 'stop'):
                module.stop()
        print("Server stopped.")

if __name__ == "__main__":
    main()
