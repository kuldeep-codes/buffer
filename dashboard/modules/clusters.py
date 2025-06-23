import os
import json
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ClustersModule:
    """
    Module for tracking cluster progress from a file
    """
    def __init__(self, config):
        """Initialize the clusters module with config"""
        self.config = config
        self.cluster_file = config.get("cluster_file", "")
        self.update_interval = config.get("update_interval", 2)
        self.data = {
            "total": 0,
            "completed": 0,
            "remaining": 0,
            "percent_str": "0.00%",
            "progress_value": 0,
            "progress_max": 1  # Avoid division by zero
        }
        self.observer = None
        self.should_stop = False
        
        # Initialize and start watching the file
        if os.path.exists(self.cluster_file):
            self.calculate_summary()
            self.start_file_watcher()
        
    def get_data(self):
        """Return the current cluster data"""
        return self.data
        
    def get_widget_html(self):
        """Return the HTML for the clusters widget"""
        return """
        <div class="widget clusters-widget">
            <h2 class="widget-title">Cluster Progress</h2>
            <div id="clusters-summary-table">
                <p>Loading clusters data...</p>
            </div>
        </div>
        """
    
    def get_widget_js(self):
        """Return the JavaScript for the clusters widget"""
        return """
        // Clusters Widget JavaScript
        function fetchAndUpdateClustersWidget() {
            fetch('/api/clusters')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    const tableDiv = document.getElementById('clusters-summary-table');
                    const percentCell = `${data.percent_str}<br><progress value='${data.progress_value}' max='${data.progress_max}'></progress>`;
                    tableDiv.innerHTML = `
                        <table>
                            <tr>
                                <th>Total</th>
                                <th>Completed</th>
                                <th>Remaining</th>
                                <th>% Completed</th>
                            </tr>
                            <tr>
                                <td>${data.total}</td>
                                <td>${data.completed}</td>
                                <td>${data.remaining}</td>
                                <td>${percentCell}</td>
                            </tr>
                        </table>
                    `;
                })
                .catch(error => {
                    console.error('Error fetching clusters data:', error);
                    const tableDiv = document.getElementById('clusters-summary-table');
                    tableDiv.innerHTML = "<p>Error loading clusters data. Is the server running?</p>";
                });
        }

        // Initialize clusters widget
        function initClustersWidget() {
            // Fetch data initially
            fetchAndUpdateClustersWidget();
            
            // Set up auto-refresh
            setInterval(fetchAndUpdateClustersWidget, 2000);
        }
        
        // Add to initialization functions
        DASHBOARD_INIT_FUNCTIONS.push(initClustersWidget);
        """

    def calculate_summary(self):
        """Reads the cluster file and updates the summary_data dictionary."""
        total = completed = 0

        if os.path.exists(self.cluster_file):
            try:
                with open(self.cluster_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line.startswith("- [ ]") or line.startswith("- [x]"):
                            total += 1
                            if line.startswith("- [x]"):
                                completed += 1
            except Exception as e:
                print(f"Error reading cluster file: {e}")
                return

        remaining = total - completed
        percent = (completed / total * 100) if total > 0 else 0
        percent_str = f"{percent:.2f}%"

        self.data = {
            "total": total,
            "completed": completed,
            "remaining": remaining,
            "percent_str": percent_str,
            "progress_value": completed,
            "progress_max": max(total, 1)  # Avoid division by zero
        }
        print("Clusters Summary Updated:", self.data)
    
    def start_file_watcher(self):
        """Start watching the cluster file for changes."""
        class FileChangeHandler(FileSystemEventHandler):
            def __init__(self, module):
                self.module = module
                
            def on_modified(self, event):
                if event.src_path == self.module.cluster_file:
                    print(f"Change detected in {self.module.cluster_file}. Recalculating summary.")
                    self.module.calculate_summary()

        if not os.path.exists(self.cluster_file):
            print(f"Warning: Cluster file does not exist: {self.cluster_file}")
            return
            
        try:
            event_handler = FileChangeHandler(self)
            self.observer = Observer()
            self.observer.schedule(event_handler, path=os.path.dirname(self.cluster_file), recursive=False)
            self.observer.start()
            print(f"Started watching for file changes in: {os.path.dirname(self.cluster_file)}")
            
            # Create a thread to keep the observer running
            def observer_thread():
                while not self.should_stop:
                    time.sleep(1)
                    
            watcher_thread = threading.Thread(target=observer_thread, daemon=True)
            watcher_thread.start()
            
        except Exception as e:
            print(f"Error starting file watcher: {e}")

    def stop(self):
        """Stop the file watcher."""
        if self.observer:
            self.should_stop = True
            self.observer.stop()
            self.observer.join()
            print("Stopped cluster file watcher")
    
    def update(self):
        """Update the data (recalculate) - called by server periodically"""
        self.calculate_summary()
        return self.data

    def get_api_routes(self):
        """Return any API routes this module needs"""
        return [
            {
                "path": "/api/clusters",
                "method": "GET",
                "handler": self.handle_api_request
            }
        ]
        
    def handle_api_request(self):
        """Handle API requests for this module"""
        return json.dumps(self.get_data())
