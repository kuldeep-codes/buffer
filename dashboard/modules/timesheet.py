import json
import time

class TimesheetModule:
    """
    Module for tracking time from Kimai API
    """
    def __init__(self, config):
        """Initialize the timesheet module with config"""
        self.config = config
        self.data = {
            "time_display": "--:--:--",
            "status": "loading",
            "status_text": "Loading timesheet data...",
            "active_timers": 0,
            "completed_entries": 0,
            "total_entries": 0,
            "last_updated": ""
        }
        
    def get_data(self):
        """Return the current timesheet data"""
        return self.data
        
    def get_widget_html(self):
        """Return the HTML for the timesheet widget"""
        return """
        <div class="widget timesheet-widget">
            <h2 class="widget-title">Today's Work Hours</h2>
            
            <div id="timesheet-time-display" class="time-display">--:--:--</div>
            
            <div id="timesheet-status" class="status loading">
                <span class="pulse">Loading timesheet data...</span>
            </div>
            
            <div id="timesheet-details" class="details" style="display: none;">
                <div>Active timers: <span id="timesheet-active-timers">0</span></div>
                <div>Completed entries: <span id="timesheet-completed-entries">0</span></div>
                <div>Total entries today: <span id="timesheet-total-entries">0</span></div>
            </div>
            
            <div id="timesheet-last-updated" class="last-updated"></div>
        </div>
        """
    
    def get_widget_js(self):
        """Return the JavaScript for the timesheet widget"""
        return f"""
        // Timesheet Widget JavaScript
        const TIMESHEET_CONFIG = {{
            domain: '{self.config["domain"]}',
            token: '{self.config["token"]}'
        }};

        let timesheetUpdateInterval;

        function formatTime(seconds) {{
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            
            return `${{hours.toString().padStart(2, '0')}}:${{minutes.toString().padStart(2, '0')}}:${{secs.toString().padStart(2, '0')}}`;
        }}

        function getTodayDateString() {{
            const today = new Date();
            return today.toISOString().split('T')[0];
        }}

        function calculateDuration(begin, end) {{
            const startTime = new Date(begin);
            const endTime = end ? new Date(end) : new Date();
            return Math.floor((endTime - startTime) / 1000);
        }}

        function isTodayEntry(begin) {{
            const entryDate = new Date(begin).toISOString().split('T')[0];
            const today = getTodayDateString();
            return entryDate === today;
        }}

        async function fetchTimesheetData() {{
            try {{
                const response = await fetch(`${{TIMESHEET_CONFIG.domain}}/api/timesheets`, {{
                    method: 'GET',
                    headers: {{
                        'Authorization': `Bearer ${{TIMESHEET_CONFIG.token}}`,
                        'Content-Type': 'application/json'
                    }}
                }});

                if (!response.ok) {{
                    throw new Error(`HTTP error! status: ${{response.status}}`);
                }}

                const data = await response.json();
                return data;
            }} catch (error) {{
                console.error('Error fetching timesheet data:', error);
                throw error;
            }}
        }}

        function updateTimesheetWidget(timesheetData) {{
            // Filter today's entries
            const todayEntries = timesheetData.filter(entry => isTodayEntry(entry.begin));
            
            let totalSeconds = 0;
            let activeTimers = 0;
            let completedEntries = 0;
            let hasActiveTimer = false;

            todayEntries.forEach(entry => {{
                if (entry.end === null) {{
                    // Active timer - calculate current duration
                    const currentDuration = calculateDuration(entry.begin, null);
                    totalSeconds += currentDuration;
                    activeTimers++;
                    hasActiveTimer = true;
                }} else {{
                    // Completed entry - use stored duration
                    totalSeconds += entry.duration;
                    completedEntries++;
                }}
            }});

            // Update display
            document.getElementById('timesheet-time-display').textContent = formatTime(totalSeconds);
            
            // Update status
            const statusEl = document.getElementById('timesheet-status');
            if (hasActiveTimer) {{
                statusEl.className = 'status active';
                statusEl.innerHTML = '<span class="pulse">⏱️ Timer Active - Working Now</span>';
            }} else if (todayEntries.length > 0) {{
                statusEl.className = 'status inactive';
                statusEl.textContent = '✅ No Active Timers';
            }} else {{
                statusEl.className = 'status inactive';
                statusEl.textContent = '📋 No work logged today';
            }}

            // Update details
            document.getElementById('timesheet-active-timers').textContent = activeTimers;
            document.getElementById('timesheet-completed-entries').textContent = completedEntries;
            document.getElementById('timesheet-total-entries').textContent = todayEntries.length;
            document.getElementById('timesheet-details').style.display = 'block';

            // Update last updated time
            document.getElementById('timesheet-last-updated').textContent = 
                `Last updated: ${{new Date().toLocaleTimeString()}}`;
        }}

        function showTimesheetError(message) {{
            const statusEl = document.getElementById('timesheet-status');
            statusEl.className = 'status error';
            statusEl.textContent = `❌ Error: ${{message}}`;
            
            document.getElementById('timesheet-time-display').textContent = '--:--:--';
            document.getElementById('timesheet-details').style.display = 'none';
        }}

        async function refreshTimesheetData() {{
            try {{
                const data = await fetchTimesheetData();
                updateTimesheetWidget(data);
            }} catch (error) {{
                showTimesheetError('Failed to fetch data. Check console for details.');
                console.error('Timesheet refresh error:', error);
            }}
        }}

        // Initialize timesheet widget
        function initTimesheetWidget() {{
            refreshTimesheetData();
            
            // Set up auto-refresh every second
            timesheetUpdateInterval = setInterval(refreshTimesheetData, 1000);
            
            // Cleanup on page unload
            window.addEventListener('beforeunload', () => {{
                if (timesheetUpdateInterval) {{
                    clearInterval(timesheetUpdateInterval);
                }}
            }});
        }}
        
        // Add to initialization functions
        DASHBOARD_INIT_FUNCTIONS.push(initTimesheetWidget);
        """

    def update(self):
        """This method would be called by an actual API consumer in a real implementation"""
        # In a real implementation, this would fetch data from the Kimai API
        # For now we'll just update the timestamp to show it's working
        self.data["last_updated"] = time.strftime("%H:%M:%S")
        return self.data

    def get_api_routes(self):
        """Return any API routes this module needs"""
        return [
            {
                "path": "/api/timesheet",
                "method": "GET",
                "handler": self.handle_api_request
            }
        ]
        
    def handle_api_request(self):
        """Handle API requests for this module"""
        return json.dumps(self.get_data())
