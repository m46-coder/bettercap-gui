# Bettercap GUI Automator

A modern Python desktop front end for automating Bettercap operations. The UI is built with CustomTkinter, communicates with Bettercap over its REST API, and falls back to `subprocess` so the same controls can be used even if the API is not yet listening.

## Project Structure

```
bettercap-gui/
├── src/
│   └── bettercap_gui/
│       ├── __init__.py
│       └── __main__.py
├── tests/
│   ├── __init__.py
│   └── test_gui.py
├── docs/
├── bettercap/        # included Bettercap source for reference
├── pyproject.toml
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Requirements

- Python 3.8 or newer (the GUI is cross-platform, so the same code runs on Linux or Windows).
- Bettercap installed and reachable from the PATH when you want to execute commands; the UI will still launch and log errors if the binary is missing so you can finish wiring interfaces before installing it.
- Dependencies: install via `pip install -r requirements.txt`.

## Installation

1. Clone this repository.
2. Create and activate a new virtual environment:
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
4. Install Bettercap separately (follow the official instructions for your platform).

## Usage

Run the GUI with `python -m bettercap_gui` or the installed `bettercap-gui` command.

### General Tab

- Set the network interface you intend to monitor.
- `Start Bettercap` launches the CLI with `api.rest on` so the GUI can talk to it.
- `Stop Bettercap` shuts the process down.
- `Refresh Modules` queries `http://127.0.0.1:8081/api/session/modules` and builds temporary tabs for each module.
- Real-time output from API commands and subprocess fallbacks are displayed in the main console.

### Spoofing Tab

- Enter comma-separated ARP targets or DNS domains for spoofing.
- Dedicated buttons start/stop ARP spoofing and DNS spoofing.
- Results and errors land in the Spoofing tab’s own console for easy debugging.
- The Spoofing job button lets you apply both ARP and DNS spoofing inputs at once, matching the CLI job you’d otherwise script.

### Recon Tab

- Enter a CIDR range or comma-separated list of hosts before starting network reconnaissance.
- Buttons control `net.recon`, `net.probe`, and `net.show` so you can shift between discovery modes with one click.
- Output is captured in the Recon tab.
- The Recon tab also includes a “Recon + ARP job” section where you can enter the CIDR and immediately kick off the combined recon/ARP spoof workflow without typing the CLI sequence.

### WiFi Tab

- Choose preferred Wi-Fi channels (e.g., `1,6,11`) so recon stays focused.
- Buttons start or stop `wifi.recon`, show nearby SSIDs, and push the channel list to Bettercap.
- Each action logs to the WiFi tab console.
- The WiFi Audit job button automates the CLI pattern: it sets the channels, starts `wifi.recon`, waits briefly, and calls `wifi.show`, mirroring the script you’d run from the original caplet.

### Workflows Tab

- The provided workflows (Recon + Spoof, WiFi Audit, Full Network Scan) execute short command sequences on a background thread so the UI stays responsive.
- A dedicated output log shows which commands ran.

### Dynamic Module Tabs

- `Refresh Modules` adds one tab per module currently loaded in Bettercap, so you can enable/disable or show module output without touching the command line.

### Output & Process Streaming

- Starting Bettercap now spawns the CLI with `stdout`/`stderr` streamed into the General tab console so you can follow its real-time output.
- The console also logs when the process terminates or when commands fail, which keeps you informed even if Bettercap was launched outside the GUI.

## Development

- Run the GUI test suite (skips on headless systems): `python -m pytest`.
- Build a distribution with `python -m build`.

## Manual Verification

1. **Linux** – after activating the venv, launch the GUI with `python -m bettercap_gui`. Click `Start Bettercap` (the console logs a friendly error if the binary is missing) and use the Recon/Spoofing/WiFi tabs or workflows to run commands once the API comes online.
2. **Windows** – run the same steps from PowerShell or inside WSL so the GUI can reach `bettercap`. Refresh modules, exercise the workflows, and confirm that the console streams stdout/stderr back into the General tab.

- The `python -m pytest` run simply instantiates the `BettercapGUI` class and will skip when no display is available, making it safe to run before Bettercap is installed.

## Notes

- Every tab has its own output area, but commands fall back to invoking `bettercap` directly if the API call fails.
- On Windows, Bettercap is usually run inside WSL or via the native release; as long as the binary is reachable from the PATH, the GUI commands will work the same way as on Linux.

### Proxy MITM Job

- The Proxies tab exposes HTTP/HTTPS listen ports so you can run the classic proxy MITM job (`http.proxy` + `https.proxy`) from the GUI without typing the CLI commands.
- `Run Proxy MITM Job` configures the ports, enables both proxies, and streams their logs back into the tab; `Stop Proxies` turns them off when you’re done.
# bettercap-gui
