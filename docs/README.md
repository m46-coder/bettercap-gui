# Bettercap GUI Documentation

## Overview

The Bettercap GUI Automator is a modern Python desktop application that provides a graphical interface for automating Bettercap operations. It uses CustomTkinter for the UI and communicates with Bettercap via its REST API.

## Features

### General Tab
- Network interface selection
- Start/Stop Bettercap process
- Stop all modules
- Refresh modules dynamically
- Real-time output console

### Spoofing Tab
- ARP spoofing with configurable targets
- DNS spoofing with configurable domains
- Combined spoofing job execution
- Dedicated output console

### Recon Tab
- Network reconnaissance with CIDR or comma-separated targets
- Network probing
- Host discovery and display
- Combined Recon + ARP job workflow

### WiFi Tab
- WiFi reconnaissance with channel selection
- WiFi device discovery
- Channel configuration
- Automated WiFi audit workflow

### Workflows Tab
- Pre-built automation workflows:
  - Recon + Spoof
  - WiFi Audit
  - Full Network Scan
  - Credential Harvest
- Progress tracking
- Workflow-specific output logging

### Events Tab
- Real-time event monitoring
- Search and filter capabilities
- Event details on double-click
- Automatic refresh (2-second intervals)

### Results Tab
- Network host table with sorting
- Context menu actions:
  - Quick/Custom port scans
  - ARP spoof targeting
  - Connection killing
  - Alias assignment
  - Note editing
  - Detailed metadata view
- Search and filter functionality

### Proxies Tab
- HTTP/HTTPS proxy configuration
- Proxy MITM job execution
- Proxy management controls

## Architecture

### Performance Optimizations

1. **HTTP Connection Pooling**: Uses `requests.Session()` for efficient connection reuse
2. **Memory Management**: Events stored in `deque(maxlen=500)` to prevent memory bloat
3. **LRU Caching**: Size formatting function cached with `@lru_cache(maxsize=128)`
4. **Thread Pool**: `ThreadPoolExecutor` with 4 workers for background tasks

### API Communication

- Base URL: `http://127.0.0.1:8081/api`
- Session endpoint: `/session`
- Modules endpoint: `/session/modules`
- Events endpoint: `/session/events`

## Usage Examples

### Starting Bettercap

```python
# Click "Start Bettercap" button in General tab
# Or programmatically:
app.start_bettercap()
```

### Running a Workflow

```python
# Click workflow button in Workflows tab
# Example: Recon + Spoof
app.run_recon_spoof_workflow()
```

### API Call Example

```python
# Fetch current session data
response = http_session.get(api_url, timeout=5)
data = response.json()
hosts = data.get('lan', {}).get('hosts', [])
```

## Development

### Running Tests

```bash
python -m pytest tests/ -v
```

Note: GUI tests require a display environment and will skip in headless environments.

### Installation

```bash
pip install -e .
```

### Running the Application

```bash
python -m bettercap_gui
# or
bettercap-gui
```

## Troubleshooting

### Common Issues

1. **Bettercap not found**: Ensure Bettercap is installed and in PATH
2. **API connection failed**: Verify Bettercap is running with REST API enabled
3. **Display errors**: GUI requires X11 display on Linux or native windowing on Windows/macOS

### Debug Mode

Check the General tab output console for real-time error messages and command output.

## Security Considerations

- Requires root/admin privileges for network operations
- Use responsibly and only on networks you own or have permission to test
- Follow local laws and regulations regarding network testing
