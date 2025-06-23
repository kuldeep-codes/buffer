# Modular Dashboard System

A flexible, modular dashboard system built with Python that allows you to display and monitor various data sources through a web interface.

## Table of Contents
- [Project Overview](#project-overview)
- [File Structure](#file-structure)
- [Configuration](#configuration)
- [Running the Dashboard](#running-the-dashboard)
- [Creating New Modules](#creating-new-modules)
- [Using with LLMs (AI Assistants)](#using-with-llms)
- [Advanced Customization](#advanced-customization)

## Project Overview

This dashboard system is designed with modularity in mind. Key features include:

- **Modular Design**: Easily add, remove or customize modules as needed
- **Grid Layout System**: Configure the exact placement and size of each widget
- **Real-Time Updates**: Widgets update automatically at configurable intervals
- **Responsive UI**: Clean, modern interface that adapts to different screen sizes
- **API Integration**: Each module can provide its own API endpoints for data retrieval
- **Extensible Design**: Easy to add new modules without modifying the core system

## File Structure

```
dashboard/
│
├── dashboard_server.py     # Main server code
├── config.json             # Dashboard configuration 
├── run_dashboard.bat       # Script to run the dashboard (Windows)
│
└── modules/                # Directory containing all modules
    ├── __init__.py
    ├── timesheet.py        # Timesheet module
    ├── clusters.py         # Clusters module
    └── ... (other modules)
```

## Configuration

The dashboard is configured using the `config.json` file:

```json
{
    "server": {
        "host": "localhost",
        "port": 8000
    },
    "grid": {
        "columns": 3,
        "cellMinWidth": 400,
        "cellMinHeight": 300
    },
    "modules": {
        "module_name": {
            "enabled": true,
            "grid": {
                "row": 0,
                "column": 0,
                "width": 600,
                "height": 400
            },
            "config": {
                // Module-specific configuration
            }
        },
        // More modules...
    }
}
```

### Configuration Options

#### Server Configuration
- `host`: The host address for the server (default: "localhost")
- `port`: The port number for the server (default: 8000)

#### Grid Configuration
- `columns`: Number of columns in the grid (default: 3)
- `cellMinWidth`: Minimum width for grid cells in pixels (default: 400)
- `cellMinHeight`: Minimum height for grid cells in pixels (default: 300)

#### Module Configuration
- `enabled`: Boolean to enable/disable the module
- `grid`: Grid positioning and sizing configuration
  - `row`: Row position (0-based index)
  - `column`: Column position (0-based index)
  - `width`: Width of the module in pixels
  - `height`: Height of the module in pixels
- `config`: Module-specific configuration parameters

## Running the Dashboard

### On Windows

Double-click the `run_dashboard.bat` file or run it from the command prompt:

```
run_dashboard.bat
```

### Manually with Python

```bash
python dashboard_server.py
```

After starting the server, access the dashboard at:
```
http://localhost:8000
```
(or whatever host/port you've configured)

## Creating New Modules

To create a new module, follow these steps:

### 1. Create a new Python file in the `modules` directory

Create a file named `your_module_name.py` in the `modules` directory.

### 2. Define a module class

The module class should follow this structure:

```python
import json
import time  # Import any required libraries

class YourModuleNameModule:
    """
    Module description
    """
    def __init__(self, config):
        """Initialize the module with config"""
        self.config = config
        self.data = {
            # Initial data structure for your module
            "key1": "value1",
            "key2": "value2",
        }
        
    def get_data(self):
        """Return the current module data"""
        return self.data
        
    def get_widget_html(self):
        """Return the HTML for the module widget"""
        return """
        <div class="widget your-module-widget">
            <h2 class="widget-title">Your Module Title</h2>
            
            <!-- Widget HTML content -->
            <div id="your-module-content">Loading...</div>
        </div>
        """
    
    def get_widget_js(self):
        """Return the JavaScript for the module widget"""
        return """
        // Your Module Widget JavaScript
        
        // Configuration from the server (if needed)
        const YOUR_MODULE_CONFIG = {
            // Access config values
        };

        function updateYourModuleWidget(data) {
            // Update widget with data
            document.getElementById('your-module-content').textContent = data.someValue;
        }

        async function fetchYourModuleData() {
            try {
                const response = await fetch('/api/your-module');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('Error fetching data:', error);
                throw error;
            }
        }

        async function refreshYourModuleData() {
            try {
                const data = await fetchYourModuleData();
                updateYourModuleWidget(data);
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('your-module-content').textContent = 'Error loading data';
            }
        }

        // Initialize widget
        function initYourModuleWidget() {
            refreshYourModuleData();
            
            // Set up auto-refresh (if needed)
            setInterval(refreshYourModuleData, 5000); // Refresh every 5 seconds
        }
        
        // Add to initialization functions
        DASHBOARD_INIT_FUNCTIONS.push(initYourModuleWidget);
        """

    def update(self):
        """Update the module data - called by server periodically"""
        # Update data here
        self.data["last_updated"] = time.strftime("%H:%M:%S")
        return self.data

    def get_api_routes(self):
        """Return any API routes this module needs"""
        return [
            {
                "path": "/api/your-module",
                "method": "GET",
                "handler": self.handle_api_request
            }
        ]
        
    def handle_api_request(self):
        """Handle API requests for this module"""
        return json.dumps(self.get_data())
```

### Important Module Requirements

1. **Class Name**: The class name must be the capitalized module name followed by "Module" (e.g., `TimesheetModule` for `timesheet.py`).

2. **Required Methods**:
   - `__init__(self, config)`: Constructor that takes a config dictionary
   - `get_widget_html()`: Returns HTML content for the widget
   - `get_widget_js()`: Returns JavaScript code for the widget
   - `get_api_routes()`: Returns a list of API routes for this module

3. **Optional Methods**:
   - `update()`: For modules that need periodic updates
   - `stop()`: For cleaning up resources when the server shuts down

### 3. Update configuration

Add your module to the `config.json` file:

```json
"your_module_name": {
    "enabled": true,
    "grid": {
        "row": 1,
        "column": 0,
        "width": 500,
        "height": 350
    },
    "config": {
        "param1": "value1",
        "param2": "value2"
    }
}
```

### 4. Restart the dashboard server

Stop the current server and restart it to load your new module.

## Using with LLMs

When using Large Language Models (like GPT) to create new modules, provide the following instructions:

### Instructions for LLMs

1. **Task**: Create a new module for the modular dashboard system.

2. **Module Name**: Specify your desired module name (e.g., "weather", "system_stats", "stock_prices").

3. **Module Purpose**: Describe what the module should display and what data it should track.

4. **Data Source**: Specify the data source (API, local file, etc.).

5. **Update Frequency**: How often should the module refresh its data.

6. **Visual Design**: Any specific visual requirements for the module.

### Example Prompt for LLM

```
Create a new dashboard module named "weather" that displays current weather conditions for a specified location.

The module should:
1. Fetch weather data from the OpenWeatherMap API
2. Display temperature, conditions, and a weather icon
3. Update every 15 minutes
4. Include a configuration parameter for the location and API key
5. Include proper error handling if the API is unavailable

The module should follow the structure required by my modular dashboard system:
- Class must be named WeatherModule
- Should have get_widget_html and get_widget_js methods
- Should define API routes for data retrieval
- Should handle the configuration properly

Also, please provide the necessary updates to the config.json file to enable this module.
```

## Advanced Customization

### Custom Styling

Each module can include custom CSS within the returned HTML. For global styles, modify the CSS in `dashboard_server.py`.

### Background Processing

For modules that need background processing:
1. Initialize a thread in the module's `__init__` method
2. Implement a `stop()` method to clean up resources
3. Use thread-safe mechanisms for data access

### Error Handling

Implement proper error handling in both Python and JavaScript. The server will catch exceptions in modules but won't crash if a module fails to load.

### Multiple Instances of the Same Module

To have multiple instances of the same module with different configurations:

1. In `config.json`, use unique keys for each instance:
```json
"weather_nyc": {
    "module_type": "weather",
    "enabled": true,
    "grid": { ... },
    "config": {
        "location": "New York",
        "units": "imperial"
    }
},
"weather_london": {
    "module_type": "weather",
    "enabled": true,
    "grid": { ... },
    "config": {
        "location": "London",
        "units": "metric"
    }
}
```

2. Modify the dashboard_server.py to support this feature by looking up the module_type attribute.

## Example Modules

The system comes with two example modules:

1. **Timesheet Module**: Tracks working hours from a time tracking API
2. **Clusters Module**: Monitors progress of tasks from a markdown file

Study these modules for examples of how to implement various features.

## Current Modules

1. **Timesheet Module**: Tracks working hours from a Kimai time tracking system
2. **Clusters Module**: Monitors task progress from a markdown file

## Configuration

Edit the `config.json` file to customize:

- Server settings (host, port)
- Grid layout (columns, minimum cell dimensions)
- Module settings (enabled/disabled, position, size, specific configuration)

Example configuration:

```json
{
    "server": {
        "host": "localhost",
        "port": 8000
    },
    "grid": {
        "columns": 3,
        "cellMinWidth": 400,
        "cellMinHeight": 300
    },
    "modules": {
        "timesheet": {
            "enabled": true,
            "grid": {
                "row": 0,
                "column": 0,
                "width": 600,
                "height": 400
            },
            "config": {
                "domain": "http://example.com",
                "token": "your-api-token"
            }
        },
        "clusters": {
            "enabled": true,
            "grid": {
                "row": 0,
                "column": 1,
                "width": 500,
                "height": 350
            },
            "config": {
                "cluster_file": "path/to/clusters.md",
                "update_interval": 2
            }
        }
    }
}
```

## Running the Dashboard

1. Make sure Python is installed
2. Double-click `run_dashboard.bat` (Windows)
3. Open a browser and navigate to http://localhost:8000 (or configured host/port)

## Creating Your Own Modules

1. Create a new Python file in the `modules` directory
2. Define a class named `[ModuleName]Module`
3. Implement the required methods:
   - `__init__(self, config)`: Initialize with configuration
   - `get_widget_html()`: Return HTML for the widget
   - `get_widget_js()`: Return JavaScript for the widget
   - `get_api_routes()`: Return API endpoints for the widget

See the existing modules for examples of implementation.

## Project Structure

```
dashboard/
├── config.json          # Configuration file
├── dashboard_server.py  # Main server code
├── run_dashboard.bat    # Batch file to run server (Windows)
├── README.md            # This file
└── modules/             # Directory for dashboard modules
    ├── __init__.py
    ├── clusters.py      # Clusters module
    └── timesheet.py     # Timesheet module
```
