import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
import subprocess
import threading
import requests
import time
import json
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BettercapGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bettercap GUI Automator")
        self.geometry("800x600")

        self.tabview = ctk.CTkTabview(self, width=780, height=550)
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)

        self.tabview.add("General")
        self.tabview.add("Workflows")
        self.tabview.add("Events")
        self.tabview.add("Results")

        general_tab = self.tabview.tab("General")
        self.interface_label = ctk.CTkLabel(general_tab, text="Network Interface:")
        self.interface_label.pack(pady=5)
        self.interface_entry = ctk.CTkEntry(general_tab)
        self.interface_entry.insert(0, "wlan0")
        self.interface_entry.pack(pady=5)

        self.start_button = ctk.CTkButton(general_tab, text="Start Bettercap", command=self.start_bettercap)
        self.start_button.pack(pady=5)
        self.stop_button = ctk.CTkButton(general_tab, text="Stop Bettercap", command=self.stop_bettercap)
        self.stop_button.pack(pady=5)

        self.stop_all_button = ctk.CTkButton(general_tab, text="Stop All Modules", command=self.stop_all_modules, fg_color="red", hover_color="darkred")
        self.stop_all_button.pack(pady=5)

        self.refresh_button = ctk.CTkButton(general_tab, text="Refresh Modules", command=self.refresh_modules)
        self.refresh_button.pack(pady=5)

        self.output_text = ctk.CTkTextbox(general_tab, wrap="word")
        self.output_text.pack(pady=10, fill="both", expand=True)

        workflow_tab = self.tabview.tab("Workflows")
        self.workflow_label = ctk.CTkLabel(workflow_tab, text="Pre-built Automation Workflows:")
        self.workflow_label.pack(pady=5)

        self.recon_spoof_button = ctk.CTkButton(
            workflow_tab, text="Recon + Spoof", command=self.run_recon_spoof_workflow
        )
        self.recon_spoof_button.pack(pady=5)

        self.wifi_audit_button = ctk.CTkButton(
            workflow_tab, text="WiFi Audit", command=self.run_wifi_audit_workflow
        )
        self.wifi_audit_button.pack(pady=5)

        self.full_scan_button = ctk.CTkButton(
            workflow_tab, text="Full Network Scan", command=self.run_full_scan_workflow
        )
        self.full_scan_button.pack(pady=5)

        self.cred_harvest_button = ctk.CTkButton(
            workflow_tab, text="Credential Harvest", command=self.run_cred_harvest_workflow
        )
        self.cred_harvest_button.pack(pady=5)
        self.workflow_buttons = [self.recon_spoof_button, self.wifi_audit_button, self.full_scan_button, self.cred_harvest_button]

        self.workflow_progress = ctk.CTkProgressBar(workflow_tab)
        self.workflow_progress.set(0)
        self.workflow_progress.pack(pady=10, fill="x", padx=10)

        self.workflow_output = ctk.CTkTextbox(workflow_tab, wrap="word")
        self.workflow_output.pack(pady=10, fill="both", expand=True)

        self.setup_spoofing_tab()
        self.setup_recon_tab()
        self.setup_wifi_tab()
        self.setup_proxy_tab()
        self.setup_events_tab()
        self.setup_results_tab()

        self.process = None
        self._workflow_running = False
        self.base_url = "http://127.0.0.1:8081/api"
        self.api_url = f"{self.base_url}/session"
        self.modules = []
        self.last_event_id = 0
        self.all_events = []
        self.events_cache = {}
        self.all_hosts = []
        self.notes_file = "host_notes.json"
        self.host_notes = self.load_notes()

    def _update_workflow_buttons_state(self):
        state = "disabled" if self._workflow_running else "normal"
        for button in self.workflow_buttons:
            button.configure(state=state)

    def _log(self, widget, message):
        widget.after(0, self._append_to_widget, widget, message)

    @staticmethod
    def _append_to_widget(widget, message):
        widget.insert("end", message)
        widget.see("end")

    def setup_spoofing_tab(self):
        self.tabview.add("Spoofing")
        tab = self.tabview.tab("Spoofing")

        ctk.CTkLabel(tab, text="ARP spoof target (comma separated):").pack(pady=3)
        self.arp_target_entry = ctk.CTkEntry(tab, placeholder_text="192.168.1.1,192.168.1.100")
        self.arp_target_entry.pack(pady=3, fill="x", padx=10)
        ctk.CTkButton(tab, text="Start ARP Spoof", command=self.start_arp_spoof).pack(pady=3)
        ctk.CTkButton(tab, text="Stop ARP Spoof", command=self.stop_arp_spoof).pack(pady=3)

        ctk.CTkLabel(tab, text="DNS spoof domains (comma separated):").pack(pady=3)
        self.dns_domains_entry = ctk.CTkEntry(tab, placeholder_text="example.com,internal.local")
        self.dns_domains_entry.pack(pady=3, fill="x", padx=10)
        ctk.CTkButton(tab, text="Start DNS Spoof", command=self.start_dns_spoof).pack(pady=3)
        ctk.CTkButton(tab, text="Stop DNS Spoof", command=self.stop_dns_spoof).pack(pady=3)

        ctk.CTkLabel(tab, text="Spoofing job: configure ARP targets and DNS domains, then run together").pack(pady=6)
        ctk.CTkButton(tab, text="Run Spoofing Job", command=self.run_spoofing_job).pack(pady=3)

        self.spoofing_output = ctk.CTkTextbox(tab, wrap="word")
        self.spoofing_output.pack(pady=10, fill="both", expand=True)

    def setup_recon_tab(self):
        self.tabview.add("Recon")
        tab = self.tabview.tab("Recon")

        ctk.CTkLabel(tab, text="Network targets (CIDR or comma separated):").pack(pady=3)
        self.recon_target_entry = ctk.CTkEntry(tab, placeholder_text="192.168.1.0/24")
        self.recon_target_entry.pack(pady=3, fill="x", padx=10)

        ctk.CTkButton(tab, text="Start Network Recon", command=self.start_network_recon).pack(pady=3)
        ctk.CTkButton(tab, text="Stop Network Recon", command=self.stop_network_recon).pack(pady=3)
        ctk.CTkButton(tab, text="Probe Network", command=self.run_network_probe).pack(pady=3)
        ctk.CTkButton(tab, text="Show Hosts", command=self.show_network_hosts).pack(pady=3)

        ctk.CTkLabel(tab, text="Recon + ARP job: configure targets and run the combined workflow").pack(pady=6)
        self.recon_job_arp_entry = ctk.CTkEntry(tab, placeholder_text="192.168.1.1,192.168.1.100")
        self.recon_job_arp_entry.pack(pady=3, fill="x", padx=10)
        ctk.CTkButton(tab, text="Run Recon + ARP Job", command=self.run_recon_arp_job).pack(pady=3)

        self.recon_output = ctk.CTkTextbox(tab, wrap="word")
        self.recon_output.pack(pady=10, fill="both", expand=True)

    def setup_wifi_tab(self):
        self.tabview.add("WiFi")
        tab = self.tabview.tab("WiFi")

        ctk.CTkLabel(tab, text="Preferred channels (comma separated):").pack(pady=3)
        self.wifi_channel_entry = ctk.CTkEntry(tab, placeholder_text="1,6,11")
        self.wifi_channel_entry.pack(pady=3, fill="x", padx=10)

        ctk.CTkButton(tab, text="Start WiFi Recon", command=self.start_wifi_recon).pack(pady=3)
        ctk.CTkButton(tab, text="Stop WiFi Recon", command=self.stop_wifi_recon).pack(pady=3)
        ctk.CTkButton(tab, text="Show WiFi Devices", command=self.show_wifi_devices).pack(pady=3)
        ctk.CTkButton(tab, text="Set WiFi Channels", command=self.update_wifi_channels).pack(pady=3)

        ctk.CTkLabel(tab, text="WiFi Audit job: sweeps channels and lists devices").pack(pady=6)
        ctk.CTkButton(tab, text="Run WiFi Audit Job", command=self.run_wifi_audit_job).pack(pady=3)

        self.wifi_output = ctk.CTkTextbox(tab, wrap="word")
        self.wifi_output.pack(pady=10, fill="both", expand=True)

    def setup_proxy_tab(self):
        self.tabview.add("Proxies")
        tab = self.tabview.tab("Proxies")

        ctk.CTkLabel(tab, text="HTTP proxy listen port:").pack(pady=3)
        self.http_port_entry = ctk.CTkEntry(tab, placeholder_text="8080")
        self.http_port_entry.pack(pady=3, fill="x", padx=10)

        ctk.CTkLabel(tab, text="HTTPS proxy listen port:").pack(pady=3)
        self.https_port_entry = ctk.CTkEntry(tab, placeholder_text="8081")
        self.https_port_entry.pack(pady=3, fill="x", padx=10)

        ctk.CTkButton(tab, text="Run Proxy MITM Job", command=self.run_proxy_mitm_job).pack(pady=6)
        ctk.CTkButton(tab, text="Stop Proxies", command=self.stop_proxy_job).pack(pady=3)

        self.proxy_output = ctk.CTkTextbox(tab, wrap="word")
        self.proxy_output.pack(pady=10, fill="both", expand=True)

    def setup_events_tab(self):
        tab = self.tabview.tab("Events")
        
        # Filter Bar
        filter_frame = ctk.CTkFrame(tab)
        filter_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        ctk.CTkLabel(filter_frame, text="Filter:").pack(side="left", padx=5)
        self.event_search_entry = ctk.CTkEntry(filter_frame, placeholder_text="Search tags or messages...")
        self.event_search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.event_search_entry.bind("<KeyRelease>", lambda e: self.apply_event_filter())
        ctk.CTkButton(filter_frame, text="Clear", width=60, command=self.clear_events).pack(side="left", padx=5)

        # Configure style for the Treeview to match dark mode
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        borderwidth=0,
                        font=('Segoe UI', 10))
        style.configure("Treeview.Heading", background="#333333", foreground="white", relief="flat")
        style.map("Treeview", background=[('selected', '#1f538d')])

        # Container for Treeview and Scrollbar
        tree_frame = ctk.CTkFrame(tab)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("time", "tag", "message")
        self.event_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')
        
        self.event_tree.heading("time", text="Time")
        self.event_tree.heading("tag", text="Tag")
        self.event_tree.heading("message", text="Event Message")
        
        self.event_tree.column("time", width=150, anchor="w")
        self.event_tree.column("tag", width=100, anchor="center")
        self.event_tree.column("message", width=500, anchor="w")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.event_tree.yview)
        self.event_tree.configure(yscrollcommand=scrollbar.set)
        
        self.event_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind double-click event to show details
        self.event_tree.bind("<Double-1>", self.on_event_double_click)

        self.after(2000, self.update_events)

    def load_notes(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_notes(self):
        try:
            with open(self.notes_file, "w") as f:
                json.dump(self.host_notes, f)
        except Exception:
            pass

    def setup_results_tab(self):
        tab = self.tabview.tab("Results")
        
        # Action Bar
        action_frame = ctk.CTkFrame(tab)
        action_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        ctk.CTkButton(action_frame, text="Refresh", width=80, command=self.fetch_results_from_api).pack(side="left", padx=5, pady=5)
        
        ctk.CTkLabel(action_frame, text="Filter:").pack(side="left", padx=5)
        self.results_search_entry = ctk.CTkEntry(action_frame, placeholder_text="Search IP, MAC or Name...")
        self.results_search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.results_search_entry.bind("<KeyRelease>", lambda e: self.apply_results_filter())

        # Container for Treeview
        tree_frame = ctk.CTkFrame(tab)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.results_columns = ("ip", "mac", "name", "vendor", "sent", "received", "seen", "note")
        self.results_tree = ttk.Treeview(tree_frame, columns=self.results_columns, show='headings', selectmode='browse')
        
        headers = {
            "ip": "IP Address", "mac": "MAC Address", "name": "Name/Alias",
            "vendor": "Vendor", "sent": "Sent", "received": "Recvd", "seen": "Last Seen",
            "note": "Notes / Discovery Info"
        }

        for col in self.results_columns:
            width = 250 if col == "note" else 100
            self.results_tree.heading(col, text=headers[col],
                                      command=lambda _col=col: self._sort_results_column(_col, False))
            self.results_tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        self.results_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Context Menu
        self.results_menu = tk.Menu(self, tearoff=0, bg="#2b2b2b", fg="white", activebackground="#1f538d")
        self.results_menu.add_command(label="Quick Port Scan (1-1000)", command=self.quick_port_scan)
        self.results_menu.add_command(label="Custom Port Scan...", command=self.custom_port_scan)
        self.results_menu.add_separator()
        self.results_menu.add_command(label="ARP Spoof Target", command=self.start_arp_spoof_on_target)
        self.results_menu.add_command(label="Kill Connection", command=self.kill_connection_on_target)
        self.results_menu.add_command(label="Set Alias...", command=self.set_alias_on_target)
        self.results_menu.add_command(label="Edit Note...", command=self.edit_note_on_target)
        self.results_menu.add_command(label="Show Detailed Metadata", command=self.show_detailed_metadata)
        self.results_tree.bind("<Button-3>", self.show_results_context_menu)
        self.results_tree.bind("<Button-2>", self.show_results_context_menu)

    def fetch_results_from_api(self):
        try:
            response = requests.get(self.api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                hosts = data.get('lan', {}).get('hosts', [])
                if 'interface' in data: hosts.append(data['interface'])
                if 'gateway' in data: hosts.append(data['gateway'])

                seen = set()
                self.all_hosts = []
                for h in hosts:
                    if h.get('mac') not in seen:
                        self.all_hosts.append(h)
                        seen.add(h.get('mac'))
                self.after(0, self.apply_results_filter)
        except Exception:
            pass

    def apply_results_filter(self):
        query = self.results_search_entry.get().lower()
        self.results_tree.delete(*self.results_tree.get_children())

        for h in self.all_hosts:
            ip = h.get('ipv4') or h.get('ip', '?.?.?.?')
            mac = h.get('mac', '??:??:??')
            name = h.get('alias') or h.get('hostname', '')
            vendor = h.get('vendor', 'unknown')
            sent = self._format_size(h.get('sent', 0))
            recvd = self._format_size(h.get('received', 0))
            seen = h.get('last_seen', '').split('.')[0].replace('T', ' ')

            # Combine User Note and Bettercap Metadata
            user_note = self.host_notes.get(mac, "")
            meta_summary = []
            meta_data = h.get('meta', {})
            if isinstance(meta_data, dict):
                # Extract discovered info (mDNS, UPnP, etc) while skipping redundant fields
                for k, v in meta_data.items():
                    if k not in ['vendor', 'hostname'] and isinstance(v, str):
                        meta_summary.append(f"{k}:{v}")
            
            display_note = f"{user_note} | {' '.join(meta_summary)}".strip(" |")

            if not query or any(query in str(v).lower() for v in [ip, mac, name, vendor, display_note]):
                self.results_tree.insert("", "end", values=(ip, mac, name, vendor, sent, recvd, seen, display_note))

    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024: return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _sort_results_column(self, col, reverse):
        data = [(self.results_tree.set(k, col), k) for k in self.results_tree.get_children('')]
        data.sort(reverse=reverse)
        for index, (val, k) in enumerate(data):
            self.results_tree.move(k, '', index)
        self.results_tree.heading(col, command=lambda: self._sort_results_column(col, not reverse))

    def show_results_context_menu(self, event):
        item = self.results_tree.identify_row(event.y)
        if item:
            self.results_tree.selection_set(item)
            self.results_menu.post(event.x_root, event.y_root)

    def edit_note_on_target(self):
        selected = self.results_tree.selection()
        if selected:
            mac = self.results_tree.item(selected[0])['values'][1]
            dialog = ctk.CTkInputDialog(text=f"Note for {mac}:", title="Edit Note")
            note = dialog.get_input()
            if note is not None:
                self.host_notes[mac] = note.strip()
                self.save_notes()
                self.apply_results_filter()

    def show_detailed_metadata(self):
        selected = self.results_tree.selection()
        if not selected: return
        mac = self.results_tree.item(selected[0])['values'][1]
        
        host_obj = next((h for h in self.all_hosts if h.get('mac') == mac), None)
        if host_obj:
            details_window = ctk.CTkToplevel(self)
            details_window.title(f"Metadata: {mac}")
            details_window.geometry("500x400")
            details_window.attributes("-topmost", True)
            text_area = ctk.CTkTextbox(details_window, wrap="word")
            text_area.pack(fill="both", expand=True, padx=10, pady=10)
            text_area.insert("0.0", json.dumps(host_obj.get('meta', {}), indent=4))
            text_area.configure(state="disabled")

    def quick_port_scan(self):
        selected = self.results_tree.selection()
        if selected:
            ip = self.results_tree.item(selected[0])['values'][0]
            self.run_api_command(f"syn.scan {ip} 1 1000")
            self.tabview.set("Recon")  # Switch to Recon tab to see progress

    def custom_port_scan(self):
        selected = self.results_tree.selection()
        if not selected:
            return
        ip = self.results_tree.item(selected[0])['values'][0]

        dialog = ctk.CTkInputDialog(text="Enter port range (e.g. 1-65535):", title="Port Scan")
        port_range = dialog.get_input()
        if port_range and "-" in port_range:
            start, end = port_range.split("-")
            self.run_api_command(f"syn.scan {ip} {start.strip()} {end.strip()}")
            self.tabview.set("Recon")

    def start_arp_spoof_on_target(self):
        selected = self.results_tree.selection()
        if selected:
            ip = self.results_tree.item(selected[0])['values'][0]
            self.run_api_command(f"set arp.spoof.targets {ip}", output_widget=self.spoofing_output)
            self.run_api_command("arp.spoof on", output_widget=self.spoofing_output)
            self.tabview.set("Spoofing")

    def kill_connection_on_target(self):
        selected = self.results_tree.selection()
        if selected:
            ip = self.results_tree.item(selected[0])['values'][0]
            self.run_api_command(f"set connection.killer.targets {ip}")
            self.run_api_command("connection.killer on")

    def set_alias_on_target(self):
        selected = self.results_tree.selection()
        if selected:
            values = self.results_tree.item(selected[0])['values']
            mac = values[1]
            dialog = ctk.CTkInputDialog(text=f"Enter alias for {mac}:", title="Set Alias")
            alias = dialog.get_input()
            if alias is not None:
                new_alias = alias.strip() if alias.strip() else '""'
                self.run_api_command(f"alias {mac} {new_alias}")

    def apply_event_filter(self):
        query = self.event_search_entry.get().lower()
        
        # Clear existing items in the Treeview
        self.event_tree.delete(*self.event_tree.get_children())
        self.events_cache.clear()

        # Re-populate Treeview from all_events based on filter (descending order)
        for ev in reversed(self.all_events):
            tag = ev.get('tag', 'info')
            msg = str(ev.get('data', ''))
            
            if not query or query in tag.lower() or query in msg.lower():
                t_str = ev.get('time', '').split('.')[0].replace('T', ' ')
                item_id = self.event_tree.insert("", "end", values=(t_str, tag, msg))
                self.events_cache[item_id] = ev

    def clear_events(self):
        self.all_events = []
        self.events_cache.clear()
        self.event_tree.delete(*self.event_tree.get_children())

    def on_event_double_click(self, event):
        selected_item = self.event_tree.selection()
        if not selected_item:
            return
        
        item_id = selected_item[0]
        event_data = self.events_cache.get(item_id)
        if event_data:
            self.show_event_details(event_data)

    def show_event_details(self, event_data):
        details_window = ctk.CTkToplevel(self)
        details_window.title("Event Details")
        details_window.geometry("600x400")
        details_window.attributes("-topmost", True)

        text_area = ctk.CTkTextbox(details_window, wrap="word")
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        text_area.insert("0.0", json.dumps(event_data, indent=4))
        text_area.configure(state="disabled")

    def refresh_modules(self):
        try:
            response = requests.get(f"{self.api_url}/modules", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.modules = data.get("modules", [])
                self.build_dynamic_tabs()
                self._log(self.output_text, f"Loaded {len(self.modules)} modules.\n")
            else:
                self._log(self.output_text, f"Failed to fetch modules: {response.status_code}\n")
        except requests.RequestException as e:
            self._log(self.output_text, f"API not available: {str(e)}\n")
        self.output_text.see("end")

    def build_dynamic_tabs(self):
        for tab_name in list(self.tabview._tab_dict.keys()):
            if tab_name not in ["General", "Workflows", "Events", "Spoofing", "Recon", "WiFi", "Proxies"]:
                self.tabview.delete(tab_name)

        for module in self.modules:
            module_name = module.get("name", "unknown")
            if module_name not in ["api.rest"]:
                tab_name = module_name.capitalize()
                self.tabview.add(tab_name)
                tab = self.tabview.tab(tab_name)
                ctk.CTkButton(tab, text=f"Enable {module_name}", command=lambda m=module_name: self.run_api_command(f"{m} on")).pack(pady=5)
                ctk.CTkButton(tab, text=f"Disable {module_name}", command=lambda m=module_name: self.run_api_command(f"{m} off")).pack(pady=5)
                ctk.CTkButton(tab, text=f"Show {module_name}", command=lambda m=module_name: self.run_api_command(f"{m}.show")).pack(pady=5)

    def run_api_command(self, cmd, output_widget=None):
        widget = output_widget or self.output_text
        try:
            response = requests.post(self.api_url, json={"cmd": cmd}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self._log(widget, f"Command: {cmd}\n{data.get('msg', '')}\n")
                else:
                    self._log(widget, f"Command failed: {cmd}\n")
            else:
                self._log(widget, f"API error: {response.status_code}\n")
        except requests.RequestException as e:
            self._log(widget, f"API not available: {str(e)}\nUse subprocess fallback.\n")
            self.run_command(["bettercap", "-eval", cmd], output_widget=widget)

    def update_events(self):
        if self.process:
            threading.Thread(target=self.fetch_events_from_api, daemon=True).start()
            threading.Thread(target=self.fetch_results_from_api, daemon=True).start()
        self.after(3000, self.update_events)

    def fetch_events_from_api(self):
        try:
            # Fetch all events from the events buffer
            response = requests.get(f"{self.base_url}/events", timeout=5)
            if response.status_code == 200:
                events = response.json()
                new_events_found = False
                for ev in events:
                    ev_id = ev.get('id', 0)
                    if ev_id > self.last_event_id:
                        self.all_events.append(ev)
                        self.last_event_id = ev_id
                        new_events_found = True
                
                if new_events_found:
                    self.after(0, self.apply_event_filter)
        except Exception:
            pass

    def run_workflow_commands(self, commands, output_widget):
        self._workflow_running = True
        self.after(0, self._update_workflow_buttons_state)
        try:
            total = len(commands)
            self.after(0, self.workflow_progress.set, 0)
            for i, cmd in enumerate(commands):
                self.run_api_command(cmd, output_widget=output_widget)
                progress = (i + 1) / total
                self.after(0, self.workflow_progress.set, progress)
                time.sleep(1)
                self._log(output_widget, f"Executed: {cmd}\n")
        finally:
            self._workflow_running = False
            self.after(0, self._update_workflow_buttons_state)

    def run_recon_arp_job(self):
        targets = self.recon_target_entry.get().strip()
        arp_targets = self.recon_job_arp_entry.get().strip()
        if targets:
            self.run_api_command(f"net.recon.targets {targets}", output_widget=self.recon_output)
        self.run_api_command("net.recon on", output_widget=self.recon_output)
        if arp_targets:
            self.run_api_command(f"arp.spoof.targets {arp_targets}", output_widget=self.spoofing_output)
        self.run_api_command("arp.spoof on", output_widget=self.spoofing_output)
        self.run_api_command("net.show", output_widget=self.recon_output)

    def run_recon_spoof_workflow(self):
        commands = [
            "net.recon on",
            "arp.spoof on",
            "net.show"
        ]
        threading.Thread(target=self.run_workflow_commands, args=(commands, self.workflow_output)).start()

    def run_wifi_audit_workflow(self):
        commands = [
            "wifi.recon on",
            "wifi.show",
            "wifi.recon.channel 1,6,11"
        ]
        threading.Thread(target=self.run_workflow_commands, args=(commands, self.workflow_output)).start()

    def run_full_scan_workflow(self):
        commands = [
            "net.recon on",
            "wifi.recon on",
            "net.probe on",
            "net.show",
            "wifi.show"
        ]
        threading.Thread(target=self.run_workflow_commands, args=(commands, self.workflow_output)).start()

    def run_cred_harvest_workflow(self):
        commands = [
            "http.proxy on",
            "https.proxy on",
            "net.recon on",
            "net.show"
        ]
        threading.Thread(target=self.run_workflow_commands, args=(commands, self.workflow_output)).start()

    def start_arp_spoof(self):
        targets = self.arp_target_entry.get().strip()
        if targets:
            self.run_api_command(f"arp.spoof.targets {targets}", output_widget=self.spoofing_output)
        self.run_api_command("arp.spoof on", output_widget=self.spoofing_output)

    def stop_arp_spoof(self):
        self.run_api_command("arp.spoof off", output_widget=self.spoofing_output)

    def start_dns_spoof(self):
        domains = self.dns_domains_entry.get().strip()
        if domains:
            self.run_api_command(f"dns.spoof.domains {domains}", output_widget=self.spoofing_output)
        self.run_api_command("dns.spoof on", output_widget=self.spoofing_output)

    def stop_dns_spoof(self):
        self.run_api_command("dns.spoof off", output_widget=self.spoofing_output)

    def run_spoofing_job(self):
        arp_targets = self.arp_target_entry.get().strip()
        dns_domains = self.dns_domains_entry.get().strip()
        if arp_targets:
            self.run_api_command(f"arp.spoof.targets {arp_targets}", output_widget=self.spoofing_output)
        self.run_api_command("arp.spoof on", output_widget=self.spoofing_output)
        if dns_domains:
            self.run_api_command(f"dns.spoof.domains {dns_domains}", output_widget=self.spoofing_output)
            self.run_api_command("dns.spoof on", output_widget=self.spoofing_output)

    def start_network_recon(self):
        targets = self.recon_target_entry.get().strip()
        if targets:
            self.run_api_command(f"net.recon.targets {targets}", output_widget=self.recon_output)
        self.run_api_command("net.recon on", output_widget=self.recon_output)

    def stop_network_recon(self):
        self.run_api_command("net.recon off", output_widget=self.recon_output)

    def run_network_probe(self):
        self.run_api_command("net.probe on", output_widget=self.recon_output)

    def show_network_hosts(self):
        self.run_api_command("net.show", output_widget=self.recon_output)

    def start_wifi_recon(self):
        channels = self.wifi_channel_entry.get().strip()
        if channels:
            self.run_api_command(f"wifi.recon.channel {channels}", output_widget=self.wifi_output)
        self.run_api_command("wifi.recon on", output_widget=self.wifi_output)

    def stop_wifi_recon(self):
        self.run_api_command("wifi.recon off", output_widget=self.wifi_output)

    def show_wifi_devices(self):
        self.run_api_command("wifi.show", output_widget=self.wifi_output)

    def update_wifi_channels(self):
        channels = self.wifi_channel_entry.get().strip()
        if channels:
            self.run_api_command(f"wifi.recon.channel {channels}", output_widget=self.wifi_output)

    def run_wifi_audit_job(self):
        channels = self.wifi_channel_entry.get().strip()
        if channels:
            self.run_api_command(f"wifi.recon.channel {channels}", output_widget=self.wifi_output)
        self.run_api_command("wifi.recon on", output_widget=self.wifi_output)
        time.sleep(1)
        self.run_api_command("wifi.show", output_widget=self.wifi_output)

    def run_proxy_mitm_job(self):
        http_port = self.http_port_entry.get().strip() or "8080"
        https_port = self.https_port_entry.get().strip() or "8081"
        self.run_api_command(f"http.proxy.listen {http_port}", output_widget=self.proxy_output)
        self.run_api_command(f"https.proxy.listen {https_port}", output_widget=self.proxy_output)
        self.run_api_command("http.proxy on", output_widget=self.proxy_output)
        self.run_api_command("https.proxy on", output_widget=self.proxy_output)

    def stop_proxy_job(self):
        self.run_api_command("http.proxy off", output_widget=self.proxy_output)
        self.run_api_command("https.proxy off", output_widget=self.proxy_output)

    def run_command(self, command, output_widget=None):
        widget = output_widget or self.output_text
        try:
            self._log(widget, f"Running: {' '.join(command)}\n")
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self._log(widget, result.stdout + result.stderr + "\n")
        except subprocess.TimeoutExpired:
            self._log(widget, "Command timed out.\n")
        except FileNotFoundError:
            messagebox.showerror("Error", "Bettercap not found. Please install Bettercap.")
        except Exception as e:
            self._log(widget, f"Error: {str(e)}\n")

    def _stream_process_output(self, proc, stream):
        if stream is None:
            return
        for line in iter(stream.readline, ""):
            if not line:
                break
            self._log(self.output_text, line)
        stream.close()
        if proc.poll() is not None and self.process is proc:
            self.process = None
            self._log(self.output_text, "Bettercap process terminated.\n")

    def start_bettercap(self):
        iface = self.interface_entry.get()
        command = ["bettercap", "-iface", iface, "-eval", "api.rest on"]
        if self.process:
            self._log(self.output_text, "Bettercap is already running.\n")
            return
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.process = process
        threading.Thread(target=self._stream_process_output, args=(process, process.stdout), daemon=True).start()
        threading.Thread(target=self._stream_process_output, args=(process, process.stderr), daemon=True).start()
        self._log(self.output_text, "Bettercap started with API.\n")

    def stop_bettercap(self):
        if self.process:
            self.process.terminate()
            self._log(self.output_text, "Bettercap stopped.\n")
            self.process = None
        else:
            self._log(self.output_text, "No Bettercap process running.\n")

    def stop_all_modules(self):
        def panic_stop():
            try:
                # Query the current state of all modules from the API
                response = requests.get(f"{self.api_url}/modules", timeout=5)
                if response.status_code == 200:
                    modules = response.json().get("modules", [])
                    # Identify running modules, excluding api.rest so we don't kill the connection
                    running = [m['name'] for m in modules if m.get('running') and m['name'] != 'api.rest']
                    
                    if running:
                        # Bettercap allows chaining commands with a semicolon for bulk execution
                        stop_command = "; ".join([f"{mod} off" for mod in running])
                        self.run_api_command(stop_command)
                        self._log(self.output_text, f"Panic stop initiated for: {', '.join(running)}\n")
                    else:
                        self._log(self.output_text, "No modules are currently active.\n")
            except Exception as e:
                self._log(self.output_text, f"Panic stop error: {e}\n")
        
        threading.Thread(target=panic_stop, daemon=True).start()


def main():
    app = BettercapGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
