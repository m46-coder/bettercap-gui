# Bettercap GUI Automator

A modern, high-performance Python desktop front end for automating Bettercap operations. The UI is built with CustomTkinter, communicates with Bettercap over its REST API, and falls back to `subprocess` so the same controls can be used even if the API is not yet listening.

## Features

- **Modern UI**: Clean, responsive interface built with CustomTkinter
- **Real-time Monitoring**: Live console output from Bettercap processes
- **Automated Workflows**: Pre-built automation scripts for common tasks
- **Dynamic Modules**: Auto-discovery and tab generation for Bettercap modules
- **Performance Optimized**: Connection pooling, memory management, LRU caching, and thread pooling
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Project Structure

```
bettercap-gui/
├── src/
│   └── bettercap_gui/
│       ├── __init__.py
│       └── __main__.py      # Main GUI application (optimized)
├── tests/
│   ├── __init__.py
│   └── test_gui.py
├── docs/
│   └── README.md
├── bettercap/               # Included Bettercap source for reference
├── dist/                    # Build artifacts (wheel & tarball)
├── pyproject.toml
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Requirements

- Python 3.8 or newer (cross-platform: Linux, macOS, Windows)
- Bettercap installed and reachable from PATH (GUI launches without it but logs errors)
- Dependencies: `pip install -r requirements.txt`

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd bettercap-gui
   ```

2. Create and activate a virtual environment:
   - **Linux/macOS**:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

3. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

4. Install Bettercap separately (follow official instructions for your platform).

5. **Alternative**: Install from built wheel:
   ```bash
   pip install dist/bettercap_gui-0.1.0-py3-none-any.whl
   ```

## Usage

Run the GUI with:
```bash
python -m bettercap_gui
```
Or use the installed command:
```bash
bettercap-gui
```

### General Tab

- **Interface Selection**: Choose the network interface to monitor
- **Start/Stop Bettercap**: Launch or terminate the Bettercap CLI with `api.rest on`
- **Refresh Modules**: Query `http://127.0.0.1:8081/api/session/modules` and generate dynamic tabs
- **Real-time Console**: View live output from API commands and subprocess fallbacks

### Spoofing Tab

- **ARP Spoofing**: Enter comma-separated targets (e.g., `192.168.1.10,192.168.1.11`)
- **DNS Spoofing**: Enter domains to spoof (e.g., `example.com,test.local`)
- **Dedicated Controls**: Start/stop ARP and DNS spoofing independently
- **Combined Job**: Apply both ARP and DNS spoofing in one action
- **Isolated Console**: Results and errors displayed in tab-specific console

### Recon Tab

- **Network Discovery**: Enter CIDR range (e.g., `192.168.1.0/24`) or comma-separated hosts
- **Recon Modes**: Control `net.recon`, `net.probe`, and `net.show`
- **Combined Workflow**: "Recon + ARP job" section for immediate recon/spoof execution
- **Tab-specific Output**: All reconnaissance results captured in dedicated console

### WiFi Tab

- **Channel Selection**: Specify channels to monitor (e.g., `1,6,11`)
- **WiFi Recon**: Start/stop `wifi.recon` with custom channel lists
- **SSID Discovery**: Execute `wifi.show` to display nearby networks
- **WiFi Audit Job**: Automated workflow: set channels → start recon → wait → show results

### Workflows Tab

Pre-built automation workflows executed on background threads:
- **Recon + Spoof**: Network discovery followed by ARP spoofing
- **WiFi Audit**: Complete WiFi reconnaissance sequence
- **Full Network Scan**: Comprehensive network mapping

Each workflow includes dedicated output logging.

### Dynamic Module Tabs

- Click `Refresh Modules` to auto-generate tabs for all loaded Bettercap modules
- Enable/disable modules and view their output without CLI interaction

### Events Tab

- **Real-time Monitoring**: Live event stream from Bettercap API
- **Filtering**: Filter events by type, severity, or keyword
- **Memory Efficient**: Uses `deque(maxlen=500)` to prevent memory bloat

### Results Tab

- **Host Table**: Display discovered hosts with IP, MAC, vendor, and alias
- **Context Menu**: Right-click for actions (ping, arpspoof, deauth, etc.)
- **Export Options**: Save results to CSV or JSON

### Proxies Tab

- **HTTP/HTTPS Proxy MITM**: Configure listen ports for proxy attacks
- **Run Proxy MITM Job**: One-click setup for `http.proxy` + `https.proxy`
- **Live Logs**: Stream proxy output to tab console
- **Stop Proxies**: Terminate proxy services cleanly

## Performance Optimizations

This application includes several performance enhancements:

1. **HTTP Connection Pooling**: Uses `requests.Session()` for efficient connection reuse across all API calls
2. **Memory Management**: Events stored in `collections.deque(maxlen=500)` to prevent unbounded memory growth
3. **LRU Caching**: `@lru_cache(maxsize=128)` decorator on size formatting function eliminates redundant calculations
4. **Thread Pool Executor**: `ThreadPoolExecutor(max_workers=4)` for efficient background task handling
5. **Asynchronous Operations**: Long-running tasks execute on background threads to maintain UI responsiveness

## Development

### Running Tests
```bash
python -m pytest
```
Tests skip automatically on headless systems (no display available).

### Building Distribution
```bash
python -m build
```
Creates wheel and source tarball in `dist/` directory.

### Installing from Source
```bash
pip install -e .
```

## Manual Verification

### Linux
1. Activate virtual environment: `source .venv/bin/activate`
2. Launch GUI: `python -m bettercap_gui`
3. Click `Start Bettercap` (logs error if binary missing)
4. Use Recon/Spoofing/WiFi tabs or workflows to execute commands
5. Verify real-time output streaming in General tab console

### Windows
1. Run from PowerShell or WSL: `.\.venv\Scripts\Activate.ps1`
2. Launch GUI: `python -m bettercap_gui`
3. Refresh modules and exercise workflows
4. Confirm stdout/stderr streaming to General tab

### Headless Testing
```bash
python -m pytest
```
Test suite safely skips GUI tests when no display is available.

## Architecture Notes

- **Fallback Mechanism**: Every tab has isolated output; commands fall back to direct `bettercap` invocation if API calls fail
- **Windows Compatibility**: Works with native Bettercap release or WSL; binary must be in PATH
- **Thread Safety**: All long-running operations execute on background threads via ThreadPoolExecutor
- **Resource Management**: Connection pooling and bounded data structures ensure efficient resource usage

## Troubleshooting

### Bettercap Not Found
- Ensure Bettercap is installed and in your system PATH
- GUI will launch and log friendly errors if binary is missing

### API Connection Failed
- Verify Bettercap is running with `api.rest on`
- Default API endpoint: `http://127.0.0.1:8081`
- Check firewall settings allow localhost connections

### No Display Available (Headless Systems)
- Tests automatically skip GUI instantiation
- Use SSH with X11 forwarding for remote GUI access

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please submit pull requests or open issues for bugs and feature requests.
