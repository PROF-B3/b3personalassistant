"""
Retro Terminal-Style GUI for B3PersonalAssistant

- Three panels: Agent Collaboration, Main User Terminal, System Control/Status
- Retro 80s computer aesthetic: black background, green text, monospace font
- Input boxes at bottom, Tab cycles between them
- /export and /clear commands, Hint button, real-time status, start/stop controls
- Optional icon support (b3_icon.ico or b3_icon.png)
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import font as tkfont
import threading
import time
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestrator import Orchestrator
from modules.resources import ResourceMonitor

RETRO_BG = "#000000"
RETRO_FG = "#00FF00"
RETRO_FONT = ("Courier New", 12)
ICON_PATHS = ["b3_icon.ico", "b3_icon.png"]

class RetroTerminalPanel(tk.Frame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, bg=RETRO_BG, **kwargs)
        self.title = title
        self.text = tk.Text(self, bg=RETRO_BG, fg=RETRO_FG, insertbackground=RETRO_FG,
                            font=RETRO_FONT, wrap=tk.WORD, borderwidth=0, highlightthickness=0)
        self.text.config(state=tk.DISABLED)
        self.text.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2,0))
        self.input_var = tk.StringVar()
        self.input_box = tk.Entry(self, textvariable=self.input_var, bg=RETRO_BG, fg=RETRO_FG,
                                  insertbackground=RETRO_FG, font=RETRO_FONT, borderwidth=0, highlightthickness=1, highlightcolor=RETRO_FG)
        self.input_box.pack(fill=tk.X, padx=2, pady=(0,2))
        self.input_box.bind("<Return>", self.on_enter)
        self.input_box.bind("<Tab>", self.on_tab)
        self.input_box.bind("<FocusIn>", lambda e: self.input_box.select_range(0, tk.END))
        self.command_callback = None
        self.export_callback = None
        self.clear_callback = None
        self.hint_callback = None
        self.panel_id = None  # For tab cycling

    def set_panel_id(self, pid):
        self.panel_id = pid

    def on_tab(self, event):
        self.master.cycle_focus(self.panel_id)
        return "break"

    def on_enter(self, event):
        cmd = self.input_var.get().strip()
        if cmd:
            if cmd.startswith("/export"):
                if self.export_callback:
                    self.export_callback()
            elif cmd.startswith("/clear"):
                self.clear()
                if self.clear_callback:
                    self.clear_callback()
            elif cmd.startswith("/hint"):
                if self.hint_callback:
                    self.hint_callback()
            else:
                if self.command_callback:
                    self.command_callback(cmd)
        self.input_var.set("")

    def append(self, text):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, text + "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def clear(self):
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)

    def export_content(self):
        content = self.text.get(1.0, tk.END)
        file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file:
            with open(file, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Export", f"Panel content exported to {file}")

class RetroGUI(tk.Tk):
    def __init__(self, user_profile=None, config=None):
        super().__init__()
        self.title("B3PersonalAssistant - Retro Terminal")
        self.configure(bg=RETRO_BG)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.resizable(True, True)
        self.geometry("1200x600")
        
        # Initialize B3PersonalAssistant system
        self.user_profile = user_profile or {}
        self.config = config
        self.orchestrator = None
        self.resource_monitor = None
        self.system_running = False
        
        self._set_icon()
        self._create_layout()
        self._setup_status_bar()
        self._setup_controls()
        self.focus_panels = [self.left_panel.input_box, self.center_panel.input_box, self.right_panel.input_box]
        for i, panel in enumerate([self.left_panel, self.center_panel, self.right_panel]):
            panel.set_panel_id(i)
        
        # Set up command callbacks
        self.center_panel.command_callback = self.process_user_input
        self.left_panel.command_callback = self.process_agent_command
        self.right_panel.command_callback = self.process_system_command
        
        self.status_updater = threading.Thread(target=self._update_status, daemon=True)
        self.status_running = True
        self.status_updater.start()
        
        # Welcome message
        self.center_panel.append("=== B3PersonalAssistant Retro Terminal ===")
        self.center_panel.append(f"Welcome, {self.user_profile.get('name', 'User')}!")
        self.center_panel.append("Type your requests in the center panel.")
        self.center_panel.append("Use /hint for help, /clear to clear, /export to save.")
        self.center_panel.append("")
        
        # Initialize agent collaboration panel
        self.left_panel.append("=== Agent Collaboration Terminal ===")
        self.left_panel.append("Available Agents:")
        self.left_panel.append("• Alpha (Α) - Chief Assistant & Coordinator")
        self.left_panel.append("• Beta (Β) - Analyst & Researcher")
        self.left_panel.append("• Gamma (Γ) - Knowledge Manager & Zettelkasten")
        self.left_panel.append("• Delta (Δ) - Task Coordinator & Workflow Manager")
        self.left_panel.append("• Epsilon (Ε) - Creative Director & Media Specialist")
        self.left_panel.append("• Zeta (Ζ) - Code Architect & Technical Specialist")
        self.left_panel.append("• Eta (Η) - Evolution Engineer & System Improvement")
        self.left_panel.append("")
        self.left_panel.append("Type agent commands in this panel.")
        self.left_panel.append("")

    def _set_icon(self):
        for path in ICON_PATHS:
            if os.path.exists(path):
                try:
                    if path.endswith(".ico"):
                        self.iconbitmap(path)
                    elif path.endswith(".png"):
                        icon = tk.PhotoImage(file=path)
                        self.iconphoto(True, icon)
                    break
                except Exception:
                    pass

    def _create_layout(self):
        self.grid_columnconfigure(0, weight=1, uniform="panel")
        self.grid_columnconfigure(1, weight=1, uniform="panel")
        self.grid_columnconfigure(2, weight=1, uniform="panel")
        self.grid_rowconfigure(0, weight=1)
        self.left_panel = RetroTerminalPanel(self, "Agent Collaboration Terminal")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(8,4), pady=8)
        self.center_panel = RetroTerminalPanel(self, "Main User Terminal")
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=4, pady=8)
        self.right_panel = RetroTerminalPanel(self, "System Control/Status Terminal")
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=(4,8), pady=8)
        # Bind export/clear/hint for each panel
        for panel in [self.left_panel, self.center_panel, self.right_panel]:
            panel.export_callback = panel.export_content
            panel.clear_callback = panel.clear
            panel.hint_callback = self.show_hints

    def _setup_status_bar(self):
        self.status_var = tk.StringVar(value="System Ready.")
        self.status_bar = tk.Label(self, textvariable=self.status_var, bg=RETRO_BG, fg=RETRO_FG, font=RETRO_FONT, anchor="w")
        self.status_bar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=8, pady=(0,4))

    def _setup_controls(self):
        self.control_frame = tk.Frame(self, bg=RETRO_BG)
        self.control_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=8, pady=(0,8))
        self.start_btn = tk.Button(self.control_frame, text="Start System", command=self.start_system, bg=RETRO_BG, fg=RETRO_FG, font=RETRO_FONT, activebackground=RETRO_BG, activeforeground=RETRO_FG, borderwidth=1, highlightbackground=RETRO_FG)
        self.stop_btn = tk.Button(self.control_frame, text="Stop System", command=self.stop_system, bg=RETRO_BG, fg=RETRO_FG, font=RETRO_FONT, activebackground=RETRO_BG, activeforeground=RETRO_FG, borderwidth=1, highlightbackground=RETRO_FG)
        self.hint_btn = tk.Button(self.control_frame, text="Hint", command=self.show_hints, bg=RETRO_BG, fg=RETRO_FG, font=RETRO_FONT, activebackground=RETRO_BG, activeforeground=RETRO_FG, borderwidth=1, highlightbackground=RETRO_FG)
        self.start_btn.pack(side=tk.LEFT, padx=4)
        self.stop_btn.pack(side=tk.LEFT, padx=4)
        self.hint_btn.pack(side=tk.LEFT, padx=4)

    def cycle_focus(self, current_panel_id):
        next_id = (current_panel_id + 1) % len(self.focus_panels)
        self.focus_panels[next_id].focus_set()

    def show_hints(self):
        hints = (
            "B3PersonalAssistant Commands:\n"
            "  /export   - Export panel content to a text file\n"
            "  /clear    - Clear panel content\n"
            "  /hint     - Show this help\n"
            "  /status   - Show system status\n"
            "  /agents   - List available agents\n"
            "\n"
            "Example requests:\n"
            "  'Research AI trends'\n"
            "  'Create a task list'\n"
            "  'Help me organize my notes'\n"
            "  'Plan my day'\n"
            "\n"
            "Tab cycles between input boxes.\n"
            "Start/Stop controls system state.\n"
        )
        messagebox.showinfo("Hints", hints)

    def start_system(self):
        try:
            if not self.system_running:
                self.orchestrator = Orchestrator(self.user_profile, self._update_gui_status)
                self.resource_monitor = ResourceMonitor(Path("databases"))
                self.system_running = True
                self.status_var.set("System Started.")
                self.center_panel.append(f"[{self._now()}] System started.")
                self.right_panel.append(f"[{self._now()}] System started.")
                self.left_panel.append(f"[{self._now()}] All agents initialized and ready.")
                self.center_panel.append("You can now interact with the AI agents!")
        except Exception as e:
            self.center_panel.append(f"[ERROR] Failed to start system: {e}")

    def stop_system(self):
        if self.system_running:
            self.system_running = False
            self.orchestrator = None
            self.resource_monitor = None
            self.status_var.set("System Stopped.")
            self.center_panel.append(f"[{self._now()}] System stopped.")
            self.right_panel.append(f"[{self._now()}] System stopped.")

    def _update_gui_status(self, message):
        """Callback for orchestrator status updates"""
        self.right_panel.append(f"[{self._now()}] {message}")

    def process_user_input(self, user_input):
        """Process user input through the orchestrator"""
        if not self.system_running:
            self.center_panel.append("System not started. Click 'Start System' first.")
            return
        
        self.center_panel.append(f"You: {user_input}")
        
        # Process in background thread to avoid blocking GUI
        def process_request():
            try:
                result = self.orchestrator.process_request(user_input)
                self.center_panel.append(f"Assistant: {result}")
            except Exception as e:
                self.center_panel.append(f"[ERROR] {e}")
        
        threading.Thread(target=process_request, daemon=True).start()

    def process_agent_command(self, command):
        """Process agent-specific commands"""
        if not self.system_running:
            self.left_panel.append("System not started. Click 'Start System' first.")
            return
        
        self.left_panel.append(f"Agent Command: {command}")
        # Add agent-specific command processing here
        self.left_panel.append("Agent commands not yet implemented.")

    def process_system_command(self, command):
        """Process system control commands"""
        if command.lower() == "/status":
            if self.system_running:
                status = self.orchestrator.get_agent_status()
                self.right_panel.append("=== System Status ===")
                for agent_name, agent_info in status['agents'].items():
                    self.right_panel.append(f"{agent_name.title()}: {agent_info['status']}")
            else:
                self.right_panel.append("System not running.")
        elif command.lower() == "/agents":
            self.right_panel.append("=== Available Agents ===")
            self.right_panel.append("Alpha (Α) - Chief Assistant & Coordinator")
            self.right_panel.append("Beta (Β) - Analyst & Researcher")
            self.right_panel.append("Gamma (Γ) - Knowledge Manager & Zettelkasten")
            self.right_panel.append("Delta (Δ) - Task Coordinator & Workflow Manager")
        else:
            self.right_panel.append(f"System Command: {command}")

    def _now(self):
        return datetime.now().strftime("%H:%M:%S")

    def _update_status(self):
        while self.status_running:
            try:
                if self.system_running and self.resource_monitor:
                    status = self.resource_monitor.get_status()
                    cpu = status.get('cpu_percent', 0)
                    memory = status.get('memory_percent', 0)
                    status_text = f"{self._now()} | System OK | Agents: 4 | CPU: {cpu:.1f}% | RAM: {memory:.1f}%"
                else:
                    status_text = f"{self._now()} | System Ready | Click 'Start System' to begin"
                self.status_var.set(status_text)
            except Exception:
                self.status_var.set(f"{self._now()} | System Status Unknown")
            time.sleep(1)

    def on_close(self):
        self.status_running = False
        if self.orchestrator:
            self.orchestrator.shutdown()
        self.destroy()

def launch_gui(config=None, user_profile=None):
    gui = RetroGUI(user_profile, config)
    gui.mainloop()

if __name__ == "__main__":
    launch_gui() 