#!/usr/bin/env python3
"""
Mainstall - Windows System Maintenance and Software Installation Tool
A professional-grade desktop application for Windows system maintenance and software installation.

Author: Mainstall
License: MIT

This script provides a Tkinter-based GUI for running maintenance tasks, installing software, and toggling system settings on Windows.
"""

import sys
import os
import ctypes
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import List, Tuple

class ToggleSwitch:
    """Custom toggle switch widget that looks like a modern slider."""
    
    def __init__(self, parent, text="", command=None, variable=None, **kwargs):
        """
        Initialize the toggle switch.
        :param parent: Parent widget
        :param text: Label text
        :param command: Function to call when toggled
        :param variable: tk.BooleanVar to bind state
        """
        self.parent = parent
        self.text = text
        self.command = command
        self.state = variable if variable is not None else tk.BooleanVar()
        
        # Create the main frame for the toggle
        self.frame = ttk.Frame(parent)
        
        # Create the label next to the toggle
        self.label = ttk.Label(self.frame, text=text, font=('Segoe UI', 10))
        self.label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create the toggle switch canvas
        self.canvas = tk.Canvas(self.frame, width=50, height=24, bg="#1e1e1e", 
                               highlightthickness=0, relief=tk.FLAT)
        self.canvas.pack(side=tk.RIGHT)
        
        # Draw the toggle switch (on/off)
        self.draw_switch()
        
        # Bind click events to toggle
        self.canvas.bind("<Button-1>", self.toggle)
        self.label.bind("<Button-1>", self.toggle)
        
    def draw_switch(self):
        """Draw the toggle switch based on current state."""
        self.canvas.delete("all")
        
        if self.state.get():
            # ON state - blue background with white circle on right
            self.canvas.create_rectangle(2, 2, 48, 22, fill="#0078d4", outline="#0078d4", width=0)
            self.canvas.create_oval(30, 4, 46, 20, fill="white", outline="white")
        else:
            # OFF state - gray background with white circle on left
            self.canvas.create_rectangle(2, 2, 48, 22, fill="#6a6a6a", outline="#6a6a6a", width=0)
            self.canvas.create_oval(4, 4, 20, 20, fill="white", outline="white")
    
    def toggle(self, event=None):
        """Toggle the switch state and call the command."""
        self.state.set(not self.state.get())
        self.draw_switch()
        if self.command:
            self.command()
    
    def get(self):
        """Get the current state (True/False)."""
        return self.state.get()
    
    def set(self, value):
        """Set the state (True/False)."""
        self.state.set(value)
        self.draw_switch()
    
    def pack(self, **kwargs):
        """Pack the frame in the parent widget."""
        return self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Unpack the frame from the parent widget."""
        return self.frame.pack_forget()

# Check if running with administrator privileges
def is_admin():
    """Check if the current process has administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-launch the script with administrator privileges using UAC."""
    if not is_admin():
        print("Requesting administrator privileges...")
        # Check if we're running as an executable or Python script
        if getattr(sys, 'frozen', False):
            # Running as executable
            executable_path = sys.executable
            print(f"Running as executable: {executable_path}")
        else:
            # Running as Python script
            executable_path = sys.executable
            print(f"Running as Python script: {executable_path}")
        
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            executable_path, 
            " ".join(sys.argv), 
            None, 
            1
        )
        sys.exit()
    else:
        print("Running with administrator privileges ✓")

class MainstallApp:
    """
    Main application class for Mainstall.
    Handles GUI creation, event handling, and command execution for maintenance, installers, quick fixes, and system settings.
    """
    
    def __init__(self):
        """
        Initialize the Mainstall application:
        - Set up system settings definitions
        - Check for admin privileges
        - Create main window and styles
        - Create all tabs and widgets
        - Set up universal mouse wheel scrolling
        """
        # System settings definitions (moved here for global access)
        self.system_settings_definitions = [
            {
                "name": "Dark Mode for Apps",
                "description": "Enable dark mode for Windows applications",
                "get_command": 'Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name AppsUseLightTheme -ErrorAction SilentlyContinue | Select-Object -ExpandProperty AppsUseLightTheme',
                "set_command_template": 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name AppsUseLightTheme -Value {value} -Type DWord -Force',
                "dark_value": "0",
                "light_value": "1",
                "reboot_required": False
            },
            {
                "name": "Show Hidden Files",
                "description": "Show hidden files and folders in File Explorer",
                "get_command": 'Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name Hidden -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Hidden',
                "set_command_template": 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name Hidden -Value {value}',
                "dark_value": "1",
                "light_value": "2",
                "reboot_required": False
            },
            {
                "name": "Clipboard History",
                "description": "Enable clipboard history (Windows + V)",
                "get_command": 'try { $val = Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Clipboard" -Name EnableClipboardHistory -ErrorAction SilentlyContinue | Select-Object -ExpandProperty EnableClipboardHistory; if ($val -eq $null) { "0" } else { $val.ToString() } } catch { "0" }',
                "set_command_template": 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Clipboard" -Name EnableClipboardHistory -Value {value} -Type DWord -Force',
                "dark_value": "1",
                "light_value": "0",
                "reboot_required": False
            },
            {
                "name": "Show File Extensions",
                "description": "Show file extensions in File Explorer",
                "get_command": 'Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name HideFileExt -ErrorAction SilentlyContinue | Select-Object -ExpandProperty HideFileExt',
                "set_command_template": 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name HideFileExt -Value {value}',
                "dark_value": "0",
                "light_value": "1",
                "reboot_required": False
            },
            {
                "name": "Disable Background Apps",
                "description": "Disable apps from running in the background",
                "get_command": 'try { $val = Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" -Name GlobalUserDisabled -ErrorAction SilentlyContinue | Select-Object -ExpandProperty GlobalUserDisabled; if ($val -eq $null) { "0" } else { $val.ToString() } } catch { "0" }',
                "set_command_template": 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" -Name GlobalUserDisabled -Value {value} -Type DWord -Force',
                "dark_value": "1",
                "light_value": "0",
                "reboot_required": False
            },
            {
                "name": "Disable Lock Screen",
                "description": "Disable the Windows lock screen",
                "get_command": 'try { $val = Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization" -Name NoLockScreen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty NoLockScreen; if ($val -eq $null) { "0" } else { $val.ToString() } } catch { "0" }',
                "set_command_template": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization" -Name NoLockScreen -Value {value} -Type DWord -Force',
                "dark_value": "1",
                "light_value": "0",
                "reboot_required": True
            },
            {
                "name": "Disable Startup Delay",
                "description": "Disable startup delay for faster boot",
                "get_command": 'try { $val = Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Serialize" -Name StartupDelayInMSec -ErrorAction SilentlyContinue | Select-Object -ExpandProperty StartupDelayInMSec; if ($val -eq $null -or $val -ne 0) { "0" } else { "1" } } catch { "0" }',
                "set_command_template": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Serialize" -Name StartupDelayInMSec -Value 0 -Type DWord -Force',
                "dark_value": "1",
                "light_value": "0",
                "reboot_required": True
            }
        ]
        self.system_settings_initialized = False
        # Check for admin privileges on startup (only if not frozen)
        if not getattr(sys, 'frozen', False):
            run_as_admin()
        
        # Create main window
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        
        # Set up universal mouse wheel scrolling for the entire application
        self.setup_universal_scrolling()
        
    def setup_window(self):
        """
        Setup the main window with proper styling and configuration:
        - Set title, size, and minimum size
        - Set window icon (ICO or PNG fallback)
        - Center the window on screen
        """
        self.root.title("Mainstall - Windows Maintenance & Software Installation")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Set window icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "mainstall.ico")
            if os.path.exists(icon_path):
                # Load and set the icon
                self.root.iconbitmap(icon_path)
            else:
                # Fallback to PNG if ICO doesn't exist
                png_path = os.path.join(os.path.dirname(__file__), "assets", "Mainstall_Image.png")
                if os.path.exists(png_path):
                    icon_image = tk.PhotoImage(file=png_path)
                    self.root.iconphoto(True, icon_image)
                    # Keep a reference to prevent garbage collection
                    self.icon_image = icon_image
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Center the window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")
        
    def setup_styles(self):
        """
        Configure dark theme styles with high contrast for all widgets.
        Sets colors, fonts, and padding for frames, buttons, tabs, labels, and scrollbars.
        """
        style = ttk.Style()
        
        # Configure dark theme colors with high contrast
        bg_color = "#1e1e1e"  # Dark background
        fg_color = "#ffffff"  # Bright white text for maximum readability
        button_bg = "#6a6a6a"  # Much lighter button background for contrast
        button_fg = "#000000"  # Black button text for contrast
        selected_bg = "#0078d4"  # Blue for selected items
        tab_bg = "#6a6a6a"  # Same light gray as buttons for consistency
        tab_fg = "#000000"  # Black tab text for contrast (same as buttons)
        
        # Configure styles with high contrast
        style.configure('TFrame', background=bg_color)
        style.configure('TNotebook', background=bg_color)
        style.configure('TNotebook.Tab', 
                       background=tab_bg, 
                       foreground=tab_fg,
                       padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'))  # Bold tab text
        style.map('TNotebook.Tab',
                 background=[('selected', selected_bg), ('active', button_bg)])
        style.configure('TButton', 
                       background=button_bg, 
                       foreground=button_fg,
                       padding=[15, 8],
                       font=('Segoe UI', 10, 'bold'))  # Bold button text
        style.map('TButton',
                 background=[('active', selected_bg), ('pressed', selected_bg)])
        
        # Special style for installer buttons
        style.configure('Installer.TButton',
                       background=button_bg,
                       foreground=button_fg,
                       padding=[12, 6],
                       font=('Segoe UI', 9, 'bold'))
        style.map('Installer.TButton',
                 background=[('active', selected_bg), ('pressed', selected_bg)])
        
        style.configure('TLabel', 
                       background=bg_color, 
                       foreground=fg_color,
                       font=('Segoe UI', 11))  # Larger, clearer label text
        style.configure('TScrollbar', 
                       background=button_bg,
                       troughcolor=bg_color,
                       width=12)
        
        # Configure main window background
        self.root.configure(bg=bg_color)
        
    def create_widgets(self):
        """
        Create and organize all GUI widgets:
        - Main frame and notebook (tab control)
        - All tabs: Maintenance, Installers, Quick Fixes, System Settings, About
        """
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.create_maintenance_tab()
        self.create_installers_tab()
        self.create_quick_fixes_tab()
        self.create_system_settings_tab()
        self.create_about_tab()
        
    def create_maintenance_tab(self):
        """
        Create the Maintenance tab with all maintenance buttons and a professional subtitle.
        Arranges buttons in two columns with tooltips and confirmation dialogs.
        """
        maintenance_frame = ttk.Frame(self.notebook)
        self.notebook.add(maintenance_frame, text="Maintenance")
        
        # Title
        title_label = ttk.Label(maintenance_frame, 
                               text="System Maintenance Tools", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(20, 2))
        # Subtitle (keep this)
        subtitle_label = ttk.Label(maintenance_frame,
                                  text="Safely perform essential Windows maintenance tasks.",
                                  font=('Segoe UI', 10),
                                  foreground="#cccccc")
        subtitle_label.pack(pady=(0, 18))
        
        # Create main content frame
        content_frame = ttk.Frame(maintenance_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Create two columns
        left_column = ttk.Frame(content_frame)
        right_column = ttk.Frame(content_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Maintenance buttons with tooltips (organized in two columns)
        maintenance_buttons = [
            ("Create Restore Point", "Checkpoint-Computer -Description 'Mainstall Restore Point' -RestorePointType 'MODIFY_SETTINGS'", "Create a Windows System Restore Point before making system changes. This allows you to roll back changes if needed."),
            ("Winget Upgrade All", "winget upgrade --all", "Update all installed winget packages to their latest versions. This will upgrade software that was installed via winget to the newest available versions."),
            ("SFC Scan (System File Checker)", "sfc /scannow", "Scan and repair corrupted Windows system files. This tool verifies the integrity of all protected system files and replaces incorrect versions with correct versions."),
            ("DISM ScanHealth", "DISM /Online /Cleanup-Image /ScanHealth", "Scan Windows image for component store corruption. This checks the Windows component store for corruption without making any repairs."),
            ("DISM CheckHealth", "DISM /Online /Cleanup-Image /CheckHealth", "Check Windows image for component store corruption. This performs a more thorough check than ScanHealth to identify corruption issues."),
            ("DISM RestoreHealth", "DISM /Online /Cleanup-Image /RestoreHealth", "Repair Windows image component store corruption. This attempts to fix corruption found by ScanHealth and CheckHealth using Windows Update as a source."),
            ("Check Disk (C:)", "chkdsk C:", "Check and repair disk errors on C: drive. This scans the file system and file system metadata for logical and physical errors."),
            ("Deep Disk Cleanup", None, "Perform comprehensive disk cleanup including DISM component cleanup, Disk Cleanup utility, and temporary file removal. This frees up significant disk space and removes system clutter."),  # Special case
            ("Clear Event Logs", "wevtutil el | ForEach-Object { wevtutil cl $_ }", "Clears all Windows Event Viewer logs. Useful after completing repairs to start fresh with system monitoring and troubleshooting."),
            ("Launch Windows Update Troubleshooter", "msdt.exe /id WindowsUpdateDiagnostic", "Launches the built-in Windows Update troubleshooter GUI. This diagnostic tool can automatically detect and fix common Windows Update issues."),
            ("Launch Network Adapter Troubleshooter", "msdt.exe /id NetworkDiagnosticsNetworkAdapter", "Launches the built-in network adapter diagnostic GUI. This tool can identify and resolve network adapter configuration problems."),
            ("Export System Info Snapshot", "Get-ComputerInfo | Out-File \"$env:USERPROFILE\\Desktop\\SystemInfo.txt\"", "Exports comprehensive system information to a text file on the user's desktop. Useful for documentation and troubleshooting purposes."),
        ]

        # Tooltip function (unchanged)
        def create_tooltip(widget, text):
            def show_tooltip(event):
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                label = tk.Label(tooltip, text=text, justify=tk.LEFT,
                               background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                               font=("Segoe UI", 9), wraplength=300)
                label.pack(padx=5, pady=5)
                screen_width = tooltip.winfo_screenwidth()
                screen_height = tooltip.winfo_screenheight()
                tooltip.update_idletasks()
                tooltip_width = tooltip.winfo_width()
                tooltip_height = tooltip.winfo_height()
                x = event.x_root + 10
                y = event.x_root + 10
                if x + tooltip_width > screen_width:
                    x = event.x_root - tooltip_width - 10
                if y + tooltip_height > screen_height:
                    y = event.x_root - tooltip_height - 10
                x = max(0, x)
                y = max(0, y)
                tooltip.wm_geometry(f"+{x}+{y}")
                def hide_tooltip(event):
                    tooltip.destroy()
                widget.bind('<Leave>', hide_tooltip)
                tooltip.bind('<Leave>', hide_tooltip)
            widget.bind('<Enter>', show_tooltip)
        
        # Distribute buttons between columns
        for i, (text, command, tooltip_text) in enumerate(maintenance_buttons):
            if text == "Deep Disk Cleanup":
                btn = ttk.Button(right_column,
                               text=text,
                               command=self.confirm_and_run_deep_disk_cleanup,
                               style='TButton',
                               width=25)
                btn.pack(fill=tk.X, pady=5)
                create_tooltip(btn, tooltip_text)
            else:
                target_column = left_column if i % 2 == 0 else right_column
                btn = ttk.Button(target_column, 
                               text=text,
                               command=lambda t=text, c=command: self.confirm_and_run_maintenance(t, c),
                               style='TButton',
                               width=25)
                btn.pack(fill=tk.X, pady=5)
                create_tooltip(btn, tooltip_text)
        
    def create_installers_tab(self):
        """
        Create the Installers tab with all software installation buttons.
        - Scrollable frame with categories and tooltips
        - Two columns per category
        - Confirmation dialog before install
        """
        installers_frame = ttk.Frame(self.notebook)
        self.notebook.add(installers_frame, text="Installers")
        
        # Set dark background for installers_frame
        installers_frame.configure(style='TFrame')
        
        # Create scrollable frame for buttons
        canvas = tk.Canvas(installers_frame, bg="#1e1e1e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(installers_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='TFrame')
        
        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", update_scroll_region)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create main container for better centering
        main_container = ttk.Frame(scrollable_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Title with improved styling
        title_label = ttk.Label(main_container, 
                               text="Software Installation", 
                               font=('Segoe UI', 18, 'bold'),
                               background="#1e1e1e", foreground="#ffffff")
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = ttk.Label(main_container,
                                  text="Select software to install with one click",
                                  font=('Segoe UI', 10),
                                  background="#1e1e1e", foreground="#cccccc")
        subtitle_label.pack(pady=(0, 30))
        
        # Software categories (alphabetically sorted)
        software_categories = {
            "Backup & Imaging": [
                ("AOMEI Backupper", "AOMEI.Backupper"),
                ("AOMEI Partition Assistant", "AOMEI.PartitionAssistant"),
                ("Macrium Reflect Free", "ParamountSoftwareUK.MacriumReflect.Free"),
                ("Ventoy", "Ventoy.Ventoy"),
                ("balenaEtcher", "Balena.Etcher"),
            ],
            "Browsers & Communication": [
                ("Brave", "Brave.Brave"),
                ("Discord", "Discord.Discord"),
                ("Google Chrome", "Google.Chrome"),
                ("Google Chrome Remote Desktop", "Google.ChromeRemoteDesktop"),
                ("Microsoft Edge", "Microsoft.Edge"),
                ("Mozilla Firefox", "Mozilla.Firefox"),
                ("Opera", "Opera.Opera"),
                ("Vivaldi", "VivaldiTechnologies.Vivaldi"),
            ],
            "Development Tools": [
                (".NET Desktop Runtime 6", "Microsoft.DotNet.DesktopRuntime.6"),
                (".NET SDK 6", "Microsoft.DotNet.SDK.6"),
                ("Atom", "GitHub.Atom"),
                ("Chocolatey", "Chocolatey.Choco"),
                ("Docker Desktop", "Docker.DockerDesktop"),
                ("Git for Windows", "Git.Git"),
                ("Java Runtime Environment", "Oracle.JavaRuntimeEnvironment"),
                ("Node.js", "OpenJS.NodeJS"),
                ("Node.js LTS", "OpenJS.NodeJS.LTS"),
                ("Postman", "Postman.Postman"),
                ("Python", "Python.Python.3.12"),
                ("Python (LTS)", "Python.Python.3"),
                ("Scoop", "ScoopInstaller.Scoop"),
                ("Sublime Text", "SublimeHQ.SublimeText.4"),
                ("Visual Studio Code", "Microsoft.VisualStudioCode"),
                ("WinMerge", "WinMerge.WinMerge"),
            ],
            "File Management": [
                ("7-Zip", "7zip.7zip"),
                ("Dropbox", "Dropbox.Dropbox"),
                ("Everything", "voidtools.Everything"),
                ("FileZilla", "FileZilla.FileZilla"),
                ("FreeFileSync", "FreeFileSync.FreeFileSync"),
                ("Google Drive", "Google.Drive"),
                ("OneDrive", "Microsoft.OneDrive"),
                ("Rufus", "Rufus.Rufus"),
                ("TeraCopy", "CodeSector.TeraCopy"),
                ("WinRAR", "RARLab.WinRAR"),
                ("WinSCP", "WinSCP.WinSCP"),
            ],
            "Gaming & Entertainment": [
                ("Battle.net", "Blizzard.BattleNet"),
                ("DOSBox", "DOSBox.DOSBox"),
                ("Epic Games Launcher", "EpicGames.EpicGamesLauncher"),
                ("GOG Galaxy", "GOG.Galaxy"),
                ("Origin", "ElectronicArts.EADesktop"),
                ("Steam", "Valve.Steam"),
                ("Ubisoft Connect", "Ubisoft.Connect"),
            ],
            "Graphics & Media": [
                ("Audacity", "Audacity.Audacity"),
                ("Blender", "BlenderFoundation.Blender"),
                ("DaVinci Resolve", "BlackmagicDesign.DaVinciResolve"),
                ("GIMP", "GIMP.GIMP"),
                ("HandBrake", "HandBrake.HandBrake"),
                ("Inkscape", "Inkscape.Inkscape"),
                ("IrfanView", "IrfanSkiljan.IrfanView"),
                ("K-Lite Codec Pack", "CodecGuide.K-LiteCodecPack.Mega"),
                ("Krita", "KDE.Krita"),
                ("Lightworks", "EditShare.Lightworks"),
                ("OBS Studio", "OBSProject.OBSStudio"),
                ("Paint.NET", "dotPDNLLC.Paint.NET"),
                ("SketchUp", "Trimble.SketchUp"),
                ("VLC Media Player", "VideoLAN.VLC"),
            ],
            "Network & Remote Access": [
                ("Advanced IP Scanner", "Famatech.AdvancedIPScanner"),
                ("Angry IP Scanner", "AngryIPScanner.AngryIPScanner"),
                ("AnyDesk", "AnyDeskSoftwareGmbH.AnyDesk"),
                ("Fiddler", "Telerik.Fiddler"),
                ("LocalSend", "localsend.Localsend"),
                ("NetWorx", "SoftPerfect.NetWorx"),
                ("nmap", "Insecure.Nmap"),
                ("OpenVPN", "OpenVPNTechnologies.OpenVPN"),
                ("ProtonVPN", "ProtonTechnologies.ProtonVPN"),
                ("PuTTY", "PuTTY.PuTTY"),
                ("Speedtest by Ookla", "Ookla.Speedtest.Desktop"),
                ("TeamViewer", "TeamViewer.TeamViewer"),
                ("Wireshark", "WiresharkFoundation.Wireshark"),
            ],
            "Office & Productivity": [
                ("Adobe Acrobat Reader", "Adobe.Acrobat.Reader.32-bit"),
                ("Adobe Acrobat Reader 64-bit", "Adobe.Acrobat.Reader.64-bit"),
                ("AutoHotkey", "AutoHotkey.AutoHotkey"),
                ("Calibre", "calibre.calibre"),
                ("Foxit Reader", "Foxit.FoxitReader"),
                ("Greenshot", "Greenshot.Greenshot"),
                ("KeePass", "KeePassXCTeam.KeePassXC"),
                ("LibreOffice", "TheDocumentFoundation.LibreOffice"),
                ("Microsoft PowerToys", "Microsoft.PowerToys"),
                ("Microsoft Teams", "Microsoft.Teams"),
                ("Notepad++", "Notepad++.Notepad++"),
                ("Obsidian", "Obsidian.Obsidian"),
                ("ONLYOFFICE Desktop Editors", "ONLYOFFICE.DesktopEditors"),
                ("ShareX", "ShareX.ShareX"),
                ("Sumatra PDF", "SumatraPDF.SumatraPDF"),
                ("Trello", "Atlassian.Trello"),
                ("Typora", "Typora.Typora"),
                ("WPS Office", "Kingsoft.WPSOffice"),
                ("Zoom", "Zoom.Zoom"),
            ],
            "Security": [
                ("Avast Free Antivirus", "AvastSoftware.AvastFreeAntivirus"),
                ("AVG AntiVirus Free", "AVGSoftware.AVG"),
                ("Bitdefender Free", "Bitdefender.Bitdefender"),
                ("Bitwarden", "Bitwarden.Bitwarden"),
                ("CCleaner", "Piriform.CCleaner"),
                ("DefenderUI", "DefenderUI.DefenderUI"),
                ("GlassWire", "SecureMixLLC.GlassWire"),
                ("Kaspersky Virus Removal Tool", "Kaspersky.VirusRemovalTool"),
                ("Malwarebytes", "Malwarebytes.Malwarebytes"),
                ("Spybot Search & Destroy", "SaferNetworkingLtd.SpybotSearchAndDestroy"),
                ("VeraCrypt", "IDRIX.VeraCrypt"),
                ("Windows Defender Exclusions Manager", "Microsoft.WindowsDefenderExclusionsManager"),
                ("Windows Firewall Control", "BiniSoft.WindowsFirewallControl"),
            ],
            "System Monitoring & Diagnostics": [
                ("AIDA64", "FinalWire.AIDA64"),
                ("Autoruns", "Microsoft.Autoruns"),
                ("Cinebench", "Maxon.Cinebench"),
                ("CPU-Z", "CPUID.CPU-Z"),
                ("CrystalDiskInfo", "CrystalDewWorld.CrystalDiskInfo"),
                ("CrystalDiskMark", "CrystalDewWorld.CrystalDiskMark"),
                ("FurMark", "Geeks3D.FurMark"),
                ("GPU-Z", "TechPowerUp.GPU-Z"),
                ("HWiNFO", "REALiX.HWiNFO"),
                ("HWMonitor", "CPUID.HWMonitor"),
                ("MemTest86", "PassMark.MemTest86"),
                ("MSI Afterburner", "Guru3D.Afterburner"),
                ("OCCT", "OCBASE.OCCT"),
                ("PC Health Check", "Microsoft.PCHealthCheck"),
                ("Prime95", "Mersenne.Prime95"),
                ("Process Explorer", "Microsoft.Sysinternals.ProcessExplorer"),
                ("Process Hacker", "ProcessHacker.ProcessHacker"),
                ("Process Monitor", "Microsoft.ProcessMonitor"),
                ("Revo Registry Cleaner", "VS Revo Group.Revo Registry Cleaner"),
                ("Revo Uninstaller", "RevoUninstaller.RevoUninstaller"),
                ("Speccy", "Piriform.Speccy"),
                ("Sysinternals Suite", "Microsoft.SysinternalsSuite"),
                ("TCPView", "Microsoft.TCPView"),
                ("VirtualBox", "Oracle.VirtualBox"),
                ("VMware Workstation Player", "VMware.WorkstationPlayer"),
                ("WinDirStat", "WinDirStat.WinDirStat"),
            ],
        }
        
        # Resort each category alphabetically by app_name
        for cat in software_categories:
            software_categories[cat] = sorted(software_categories[cat], key=lambda x: x[0].lower())
        
        # Create category sections in alphabetical order
        for category_name in sorted(software_categories.keys()):
            software_list = software_categories[category_name]
            
            # Create category container with better spacing
            category_container = ttk.Frame(main_container)
            category_container.pack(fill=tk.X, pady=(0, 25))
            
            # Category header with improved styling
            category_header_frame = ttk.Frame(category_container)
            category_header_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Category title with icon-like styling
            category_label = ttk.Label(category_header_frame, 
                                     text=f"📁 {category_name}", 
                                     font=('Segoe UI', 14, 'bold'),
                                     background="#1e1e1e", foreground="#ffffff")
            category_label.pack(anchor=tk.W)
            
            # Create a more visible separator using a different approach
            separator_canvas = tk.Canvas(category_header_frame, height=1, bg="#404040", highlightthickness=0)
            separator_canvas.pack(fill=tk.X, pady=(8, 0))
            
            # Create centered content area for this category
            content_area = ttk.Frame(category_container)
            content_area.pack(expand=True)
            
            # Create two columns for this category with better spacing
            left_column = ttk.Frame(content_area)
            right_column = ttk.Frame(content_area)
            
            left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
            right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))
            
            # Create tooltip function for installers
            def create_tooltip(widget, text):
                def show_tooltip(event):
                    tooltip = tk.Toplevel()
                    tooltip.wm_overrideredirect(True)
                    
                    # Create label to measure text size
                    label = tk.Label(tooltip, text=text, justify=tk.LEFT,
                                   background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                                   font=("Segoe UI", 9), wraplength=300)  # Wrap text to prevent wide tooltips
                    label.pack(padx=5, pady=5)
                    
                    # Get screen dimensions
                    screen_width = tooltip.winfo_screenwidth()
                    screen_height = tooltip.winfo_screenheight()
                    
                    # Calculate tooltip dimensions
                    tooltip.update_idletasks()
                    tooltip_width = tooltip.winfo_width()
                    tooltip_height = tooltip.winfo_height()
                    
                    # Calculate initial position (10 pixels offset from cursor)
                    x = event.x_root + 10
                    y = event.y_root + 10
                    
                    # Adjust horizontal position if tooltip would go off screen
                    if x + tooltip_width > screen_width:
                        x = event.x_root - tooltip_width - 10
                    
                    # Adjust vertical position if tooltip would go off screen
                    if y + tooltip_height > screen_height:
                        y = event.y_root - tooltip_height - 10
                    
                    # Ensure tooltip doesn't go off the left or top edges
                    x = max(0, x)
                    y = max(0, y)
                    
                    tooltip.wm_geometry(f"+{x}+{y}")
                    
                    def hide_tooltip(event):
                        tooltip.destroy()
                    
                    widget.bind('<Leave>', hide_tooltip)
                    tooltip.bind('<Leave>', hide_tooltip)
                
                widget.bind('<Enter>', show_tooltip)
            
            # Software tooltips dictionary
            software_tooltips = {
                # Backup & Imaging
                "AOMEI Backupper": "Comprehensive backup software for Windows. Supports system, disk, file, and partition backup and restore with scheduling and encryption.",
                "AOMEI Partition Assistant": "Disk partition management tool for resizing, merging, splitting, and migrating partitions safely without data loss.",
                "Macrium Reflect Free": "Reliable disk imaging and backup solution for creating full, incremental, and differential backups with disaster recovery.",
                "Ventoy": "Tool for creating multiboot USB drives with multiple ISO files. Drag-and-drop simplicity for bootable media creation.",
                "balenaEtcher": "Easy-to-use tool for flashing OS images to SD cards and USB drives. Cross-platform and open-source with verification.",
                
                # Browsers & Communication
                "Brave": "Privacy-focused web browser with built-in ad blocker, tracking protection, and crypto wallet. Fast, secure, and open-source.",
                "Discord": "Voice, video, and text communication platform for gamers and communities. Features include server creation, voice channels, screen sharing, and file sharing.",
                "Google Chrome": "Fast, secure web browser with extensive extension support and Google integration. Features include automatic updates, built-in security, incognito mode, and cross-device sync.",
                "Google Chrome Remote Desktop": "Remote desktop tool for accessing computers securely over the internet using Chrome browser or app.",
                "Microsoft Edge": "Microsoft's Chromium-based browser with strong security, performance, and integration with Windows 10/11 features.",
                "Mozilla Firefox": "Privacy-focused web browser with customizable features, strong security, and open-source transparency.",
                "Opera": "Feature-rich web browser with built-in VPN, ad blocker, and social integrations. Known for speed and customization.",
                "Vivaldi": "Highly customizable web browser with advanced tab management, built-in tools, and privacy features.",
                
                # Development Tools
                ".NET Desktop Runtime 6": "Microsoft's runtime for running Windows desktop applications built with .NET 6.",
                ".NET SDK 6": "Software development kit for building .NET 6 applications. Includes compilers, libraries, and tools.",
                "Atom": "Hackable text editor for the 21st century, developed by GitHub. Supports plugins, themes, and collaborative coding.",
                "Chocolatey": "Windows package manager for installing, updating, and managing software via command line.",
                "Docker Desktop": "Containerization platform for building, sharing, and running containerized applications on Windows.",
                "Git for Windows": "Distributed version control system for tracking code changes and collaboration. Essential for software development.",
                "Java Runtime Environment": "Environment required to run Java applications. Includes JVM, core libraries, and supporting files.",
                "Node.js": "JavaScript runtime for building scalable network applications. Used for web servers, tools, and scripts.",
                "Node.js LTS": "Long-term support version of Node.js for maximum stability and compatibility.",
                "Postman": "API development environment for building, testing, and documenting APIs. Supports automation and collaboration.",
                "Python": "High-level programming language for web development, data analysis, automation, and more. Known for simplicity and versatility.",
                "Python (LTS)": "Long-term support version of Python for maximum compatibility.",
                "Scoop": "Command-line installer for Windows, focused on simplicity and developer tools.",
                "Sublime Text": "Sophisticated text editor for code, markup, and prose. Fast, lightweight, and extensible.",
                "Visual Studio Code": "Powerful, extensible code editor with IntelliSense, debugging, and Git integration.",
                "WinMerge": "File and folder comparison tool for merging and visualizing differences. Useful for code reviews and backups.",
                
                # File Management
                "7-Zip": "High-compression file archiver supporting 7z, ZIP, RAR, and more. Free, open-source, and trusted for secure file compression.",
                "Dropbox": "Cloud storage and file synchronization service for sharing and backing up files across devices.",
                "Everything": "Ultra-fast file search tool for Windows. Instantly locates files and folders by name.",
                "FileZilla": "Cross-platform FTP, FTPS, and SFTP client for secure file transfers between local and remote servers.",
                "FreeFileSync": "Folder comparison and synchronization tool for backups and file management.",
                "Google Drive": "Cloud storage and collaboration platform by Google. Syncs files across devices and integrates with Google Workspace.",
                "OneDrive": "Microsoft's cloud storage solution for file backup, sharing, and collaboration.",
                "Rufus": "Utility for creating bootable USB drives from ISO files. Supports UEFI and legacy boot modes.",
                "TeraCopy": "File transfer utility with pause/resume, error recovery, and file verification. Faster and more reliable than Windows copy.",
                "WinRAR": "Popular file compression and archiving utility with strong encryption and multi-format support.",
                "WinSCP": "SFTP, FTP, WebDAV, and SCP client for secure file transfer and management.",
                
                # Gaming & Entertainment
                "Battle.net": "Game launcher and platform for Blizzard games. Includes social features and automatic updates.",
                "DOSBox": "Emulator for running classic DOS games and applications on modern systems.",
                "Epic Games Launcher": "Game distribution platform with free weekly games and exclusive titles.",
                "GOG Galaxy": "Game client for DRM-free games from GOG.com. Unified library and social features.",
                "Origin": "EA's game platform for purchasing, downloading, and playing games. Includes cloud saves and social features.",
                "Steam": "World's largest digital distribution platform for PC games. Features cloud saves, achievements, and community.",
                "Ubisoft Connect": "Ubisoft's game launcher and social platform for PC games, achievements, and rewards.",
                
                # Graphics & Media
                "Audacity": "Open-source audio editor and recorder with multi-track editing, effects, and analysis tools.",
                "Blender": "Professional 3D modeling, animation, and rendering suite. Free and open-source.",
                "DaVinci Resolve": "Professional video editing, color correction, and audio post-production software.",
                "GIMP": "Free image editor with advanced features for photo retouching, image composition, and creation.",
                "HandBrake": "Open-source video transcoder for converting video files between formats.",
                "Inkscape": "Vector graphics editor for creating scalable illustrations, logos, and diagrams.",
                "IrfanView": "Lightweight image viewer and editor with batch processing and format conversion.",
                "K-Lite Codec Pack": "Comprehensive collection of audio and video codecs for media playback.",
                "Krita": "Digital painting and illustration software for artists. Supports advanced brush engines and color management.",
                "Lightworks": "Professional video editing software with real-time effects and multi-format support.",
                "OBS Studio": "Open-source software for video recording and live streaming. Supports multiple sources and scenes.",
                "Paint.NET": "User-friendly image and photo editor with layers, effects, and plugin support.",
                "SketchUp": "3D modeling software for architectural, interior design, and engineering projects.",
                "VLC Media Player": "Versatile media player supporting virtually all audio and video formats. Reliable and open-source.",
                
                # Network & Remote Access
                "Advanced IP Scanner": "Network scanner for discovering devices and analyzing network infrastructure.",
                "Angry IP Scanner": "Fast and friendly network scanner for scanning IP addresses and ports.",
                "AnyDesk": "Remote desktop software for secure remote access and support. Fast, lightweight, and cross-platform.",
                "Fiddler": "Web debugging proxy for inspecting and modifying HTTP(S) traffic.",
                "LocalSend": "Secure, private file sharing app for local networks. No server required.",
                "NetWorx": "Bandwidth monitoring and usage reporting tool for Windows.",
                "OpenVPN": "Open-source VPN client for secure internet access and privacy.",
                "ProtonVPN": "Privacy-focused VPN service with strong encryption and no-logs policy.",
                "PuTTY": "SSH and telnet client for secure remote connections to servers and network devices.",
                "Speedtest by Ookla": "Official desktop app for testing internet speed and connection quality.",
                "TeamViewer": "Remote control and file transfer software with enterprise-grade security.",
                "Wireshark": "Network protocol analyzer for troubleshooting and analyzing network traffic.",
                
                # Office & Productivity
                "Adobe Acrobat Reader": "Industry-standard PDF viewer with annotation, form filling, and digital signature support.",
                "Adobe Acrobat Reader 64-bit": "64-bit version of Adobe's industry-standard PDF viewer.",
                "AutoHotkey": "Powerful scripting language for automating Windows tasks and creating custom hotkeys.",
                "Calibre": "E-book management software for organizing, converting, and reading e-books.",
                "Foxit Reader": "Lightweight, fast, and secure PDF reader with annotation and collaboration features.",
                "Greenshot": "Screenshot tool with annotation, editing, and sharing capabilities.",
                "KeePass": "Open-source password manager with strong encryption and local storage.",
                "LibreOffice": "Full-featured open-source office suite compatible with Microsoft Office formats.",
                "Microsoft PowerToys": "Utilities for power users to enhance productivity and customize Windows.",
                "Microsoft Teams": "Collaboration platform for chat, meetings, and file sharing in organizations.",
                "Notepad++": "Advanced text editor with syntax highlighting, multi-document editing, and plugin support.",
                "Obsidian": "Knowledge base and note-taking app with markdown support and graph view.",
                "ONLYOFFICE Desktop Editors": "Office suite for editing text documents, spreadsheets, and presentations.",
                "ShareX": "Screen capture, file sharing, and productivity tool with extensive customization.",
                "Sumatra PDF": "Lightweight PDF, eBook, and comic book reader for Windows.",
                "Trello": "Visual project management tool using boards, lists, and cards for task organization.",
                "Typora": "Minimalist markdown editor with live preview and export options.",
                "WPS Office": "Office suite with word processor, spreadsheet, and presentation tools. Compatible with Microsoft Office.",
                "Zoom": "Video conferencing and online meeting platform with screen sharing and recording.",
                
                # Security
                "Avast Free Antivirus": "Comprehensive antivirus protection with real-time scanning and threat detection.",
                "AVG AntiVirus Free": "Popular antivirus with file and web protection, plus performance optimization.",
                "Bitdefender Free": "Advanced antivirus with behavioral detection and minimal system impact.",
                "Bitwarden": "Open-source password manager with end-to-end encryption and cross-platform support.",
                "CCleaner": "System optimization and privacy protection tool with registry cleaning and startup management.",
                "DefenderUI": "Enhanced interface for Windows Defender settings and configuration.",
                "GlassWire": "Network monitoring and firewall visualization with security alerts.",
                "Kaspersky Virus Removal Tool": "Free tool for scanning and removing viruses and malware from Windows systems.",
                "Malwarebytes": "Anti-malware software for threat detection and removal with real-time protection.",
                "Spybot Search & Destroy": "Anti-spyware and registry protection with immunization features.",
                "VeraCrypt": "Open-source disk encryption software for securing files, partitions, and entire drives.",
                "Windows Defender Exclusions Manager": "Tool for managing Windows Defender exclusions and security settings.",
                "Windows Firewall Control": "Enhanced Windows Firewall management with advanced configuration options.",
                
                # System Monitoring & Diagnostics
                "AIDA64": "Comprehensive system information, diagnostics, and benchmarking tool for Windows.",
                "Autoruns": "Shows what programs are configured to run during system bootup or login.",
                "Cinebench": "CPU and GPU benchmarking tool for evaluating hardware performance.",
                "CPU-Z": "System information and hardware monitoring tool with detailed component analysis.",
                "CrystalDiskInfo": "Disk health monitoring tool for HDDs and SSDs. Displays SMART status and temperature.",
                "CrystalDiskMark": "Benchmarking tool for measuring disk read/write speeds.",
                "FurMark": "GPU stress testing and benchmarking tool for graphics cards.",
                "GPU-Z": "Lightweight utility for monitoring graphics card details and sensors.",
                "HWiNFO": "Comprehensive hardware analysis and monitoring with detailed system information.",
                "HWMonitor": "Hardware monitoring program that reads PC systems' main health sensors.",
                "MemTest86": "Memory testing tool for diagnosing RAM errors and stability issues.",
                "MSI Afterburner": "Overclocking utility for graphics cards with monitoring and fan control.",
                "OCCT": "Stability checking and stress testing tool for CPUs, GPUs, and power supplies.",
                "PC Health Check": "Microsoft's tool for checking Windows 11 compatibility and system health.",
                "Prime95": "CPU stress testing and benchmarking tool, popular for stability testing.",
                "Process Explorer": "Advanced process management utility from Sysinternals for Windows.",
                "Process Hacker": "Powerful multi-purpose tool for managing processes and services.",
                "Process Monitor": "Real-time file system, Registry, and process/thread activity monitoring tool.",
                "Revo Registry Cleaner": "Registry cleaning and optimization tool with backup and restore features.",
                "Revo Uninstaller": "Complete software removal tool with leftover cleanup and advanced uninstallation.",
                "Speccy": "Detailed system information tool for PC hardware and temperature monitoring.",
                "Sysinternals Suite": "Collection of advanced system utilities from Microsoft for troubleshooting and diagnostics.",
                "TCPView": "Shows detailed listings of all TCP and UDP endpoints on your system.",
                "VirtualBox": "Open-source virtualization platform for running multiple operating systems on one machine.",
                "VMware Workstation Player": "Virtualization software for running multiple operating systems as virtual machines.",
                "WinDirStat": "Disk usage statistics and cleanup tool with visual file analysis.",
            }
            
            # Distribute buttons between columns with uniform sizing and tooltips
            for i, (app_name, app_id) in enumerate(software_list):
                btn = ttk.Button(
                    left_column if i % 2 == 0 else right_column,
                    text=app_name,
                    command=lambda name=app_name, id=app_id: self.install_software(name, id),
                    style='Installer.TButton',
                    width=32  # Slightly wider buttons for better appearance
                )
                btn.pack(fill=tk.X, pady=3, padx=8)  # Better spacing between buttons
                
                # Add tooltip for this software
                tooltip_text = software_tooltips.get(app_name, f"Install {app_name}")
                create_tooltip(btn, tooltip_text)
        
        # Pack canvas and scrollbar with better proportions
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 20))
        
        # Ensure content starts at the top and update scroll region
        canvas.update_idletasks()
        canvas.yview_moveto(0)
        
    def create_quick_fixes_tab(self):
        """
        Create the Quick Fixes tab with common troubleshooting buttons.
        Arranges buttons in two columns with tooltips and confirmation dialogs.
        """
        quick_fixes_frame = ttk.Frame(self.notebook)
        self.notebook.add(quick_fixes_frame, text="Quick Fixes")
        
        # Title
        title_label = ttk.Label(quick_fixes_frame, 
                               text="Quick System Fixes", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(20, 2))
        # Subtitle
        subtitle_label = ttk.Label(quick_fixes_frame,
                                  text="Quickly resolve common Windows issues with one click.",
                                  font=('Segoe UI', 10),
                                  foreground="#cccccc")
        subtitle_label.pack(pady=(0, 18))
        
        # Create main content frame
        content_frame = ttk.Frame(quick_fixes_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Create two columns
        left_column = ttk.Frame(content_frame)
        right_column = ttk.Frame(content_frame)
        
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Quick fixes buttons with tooltips
        quick_fixes_buttons = [
            ("Flush DNS Cache", "ipconfig /flushdns", "Clear the DNS resolver cache to resolve network connectivity issues. This forces Windows to query DNS servers for fresh information instead of using cached data."),
            ("Restart Windows Explorer", "Stop-Process -Name explorer -Force", "Restart Windows Explorer to fix UI issues and freezes. This refreshes the desktop, taskbar, and file explorer without requiring a full system restart."),
            ("Clear Microsoft Store Cache", "wsreset.exe", "Clear Microsoft Store cache to fix download and update issues. This removes corrupted cache files that may prevent apps from downloading or updating properly."),
            ("Kill High-CPU Background Tasks", "Get-Process | Where-Object { $_.CPU -gt 30 } | Stop-Process -Force", "Terminate processes using more than 30% CPU to improve performance. This helps identify and stop resource-intensive background processes that may be slowing down your system."),
            ("Clear Clipboard", 'cmd /c "echo off | clip"', "Clear the Windows clipboard to free memory and resolve clipboard issues. This removes any data stored in the clipboard and can help resolve copy/paste problems."),
            ("Clear Temp Files", r'Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue', "Remove temporary files to free disk space and improve performance. This deletes files that applications no longer need, potentially freeing up several gigabytes of space."),
            ("Reset Windows Update", "net stop wuauserv; net stop cryptSvc; net stop bits; net stop msiserver; ren C:\\Windows\\SoftwareDistribution SoftwareDistribution.old; ren C:\\Windows\\System32\\catroot2 catroot2.old; net start wuauserv; net start cryptSvc; net start bits; net start msiserver", "Reset Windows Update services and clear update cache to fix update issues. This stops update services, renames cache folders, and restarts services to resolve update problems."),
            ("Fix Windows Search", "Get-AppXPackage -Name Microsoft.Windows.Search -AllUsers | Reset-AppxPackage", "Reset Windows Search to fix search functionality issues. This reinstalls the Windows Search component to resolve problems with the search feature."),
            ("Clear Print Queue", 'net stop spooler; Remove-Item "$env:windir\\System32\\spool\\PRINTERS\\*" -Recurse; net start spooler', "Clear print queue and restart print spooler to fix printing issues. This stops the print service, removes stuck print jobs, and restarts the service."),
            ("Restart Network Adapter", "Get-NetAdapter | Restart-NetAdapter -Confirm:$false", "Restart all network adapters to fix network connectivity issues. This refreshes network connections and can resolve internet connectivity problems."),
            ("Fix Store Apps", 'Get-AppXPackage -AllUsers | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\\AppXManifest.xml"}', "Repair Microsoft Store apps by re-registering all installed apps. This fixes apps that may be corrupted or not functioning properly."),
            ("Restart Windows Explorer (Command Version)", 'cmd /c "taskkill /f /im explorer.exe && start explorer.exe"', "Fully restarts File Explorer and UI shell components using command line. This alternative method can resolve explorer issues when the PowerShell method fails."),
            ("Restart Print Spooler Only", "net stop spooler && net start spooler", "Fixes stuck print jobs or printing issues without clearing the queue. This restarts the print service while preserving pending print jobs."),
            ("Restart Windows Update Service", "net stop wuauserv && net start wuauserv", "Resets Windows Update service quickly without cache clearance. This is a faster alternative to the full Windows Update reset for minor update issues."),
        ]
        
        # Create tooltip function
        def create_tooltip(widget, text):
            def show_tooltip(event):
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                
                # Create label to measure text size
                label = tk.Label(tooltip, text=text, justify=tk.LEFT,
                               background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                               font=("Segoe UI", 9), wraplength=300)
                label.pack(padx=5, pady=5)
                
                # Get screen dimensions
                screen_width = tooltip.winfo_screenwidth()
                screen_height = tooltip.winfo_screenheight()
                
                # Calculate tooltip dimensions
                tooltip.update_idletasks()
                tooltip_width = tooltip.winfo_width()
                tooltip_height = tooltip.winfo_height()
                
                # Calculate initial position (10 pixels offset from cursor)
                x = event.x_root + 10
                y = event.y_root + 10
                
                # Adjust horizontal position if tooltip would go off screen
                if x + tooltip_width > screen_width:
                    x = event.x_root - tooltip_width - 10
                
                # Adjust vertical position if tooltip would go off screen
                if y + tooltip_height > screen_height:
                    y = event.y_root - tooltip_height - 10
                
                # Ensure tooltip doesn't go off the left or top edges
                x = max(0, x)
                y = max(0, y)
                
                tooltip.wm_geometry(f"+{x}+{y}")
                
                def hide_tooltip(event):
                    tooltip.destroy()
                
                widget.bind('<Leave>', hide_tooltip)
                tooltip.bind('<Leave>', hide_tooltip)
            
            widget.bind('<Enter>', show_tooltip)
        
        # Distribute buttons between columns
        for i, (text, command, tooltip_text) in enumerate(quick_fixes_buttons):
            target_column = left_column if i % 2 == 0 else right_column
            btn = ttk.Button(target_column, 
                           text=text,
                           command=lambda t=text, c=command: self.confirm_and_run_quick_fix(t, c),
                           style='TButton',
                           width=25)
            btn.pack(fill=tk.X, pady=5)
            create_tooltip(btn, tooltip_text)

    def create_system_settings_tab(self):
        """
        Create the System Settings tab with toggle switches for common settings.
        Arranges toggles in two columns, each with a description label.
        """
        system_settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_settings_frame, text="System Settings")
        
        # Title
        title_label = ttk.Label(system_settings_frame, 
                               text="System Settings", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(20, 2))
        # Subtitle
        subtitle_label = ttk.Label(system_settings_frame,
                                  text="Toggle common Windows settings for privacy, appearance, and performance.",
                                  font=('Segoe UI', 10),
                                  foreground="#cccccc")
        subtitle_label.pack(pady=(0, 10))
        
        # Refresh button
        refresh_btn = ttk.Button(system_settings_frame, text="Refresh", command=self.initialize_system_settings_states)
        refresh_btn.pack(pady=(0, 15))
        
        # Create main content frame
        content_frame = ttk.Frame(system_settings_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Create two columns
        left_column = ttk.Frame(content_frame)
        right_column = ttk.Frame(content_frame)
        
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Create settings toggles
        self.settings_vars = {}
        self.settings_widgets = {}
        
        for i, setting in enumerate(self.system_settings_definitions):
            target_column = left_column if i % 2 == 0 else right_column
            
            # Create frame for this setting
            setting_frame = ttk.Frame(target_column)
            setting_frame.pack(fill=tk.X, pady=8, padx=5)
            
            # Create variable for the toggle
            var = tk.BooleanVar()
            self.settings_vars[setting["name"]] = var
            
            # Create toggle switch, passing the variable
            toggle_switch = ToggleSwitch(
                setting_frame,
                text=setting["name"],
                command=lambda s=setting, v=var: self.toggle_setting(s, v),
                variable=var
            )
            toggle_switch.pack(anchor=tk.W, fill=tk.X)
            
            # Create description label
            desc_label = ttk.Label(
                setting_frame,
                text=setting["description"],
                font=('Segoe UI', 9),
                foreground="#cccccc"
            )
            desc_label.pack(anchor=tk.W, padx=(0, 0), pady=(5, 0))
            
            # Store widget reference
            self.settings_widgets[setting["name"]] = toggle_switch
            
            # Store setting reference for later initialization
            setting["var"] = var
        
    def create_about_tab(self):
        """
        Create the About tab with app logo/image, app info, GitHub link, and copyright.
        Shows image at the top, then app name, version, author, license, support, and copyright.
        """
        about_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(about_frame, text="About")

        # Main container for About content
        main_container = ttk.Frame(about_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # App Logo/Image Section
        logo_frame = ttk.Frame(main_container)
        logo_frame.pack(pady=(0, 10))
        try:
            import os
            img_path = os.path.join(os.path.dirname(__file__), "assets", "Mainstall_Image_128.png")
            if os.path.exists(img_path):
                self.mainstall_img = tk.PhotoImage(file=img_path)
                img_label = ttk.Label(logo_frame, image=self.mainstall_img, background="#1e1e1e")
                img_label.pack()
            else:
                raise FileNotFoundError(f"Image not found at {img_path}")
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Image Load Error", f"Failed to load Mainstall_Image_128.png:\n{e}\nIf the image is too large, resize it to a max width of 120px using an image editor.")
            icon_label = ttk.Label(
                logo_frame,
                text="🔧",
                font=("Segoe UI", 36),
                background="#1e1e1e",
                foreground="#0078d4"
            )
            icon_label.pack()

        # App Name and Tagline
        app_name_label = ttk.Label(
            main_container,
            text="Mainstall",
            font=("Segoe UI", 22, "bold"),
            background="#1e1e1e",
            foreground="#ffffff"
        )
        app_name_label.pack(pady=(0, 2))
        tagline_label = ttk.Label(
            main_container,
            text="Professional Windows Maintenance & Software Installation Tool",
            font=("Segoe UI", 10),
            background="#1e1e1e",
            foreground="#cccccc"
        )
        tagline_label.pack(pady=(0, 10))

        # Compact Info Row (Version | Author | License)
        info_row = ttk.Frame(main_container)
        info_row.pack(pady=(0, 10))
        version_icon = ttk.Label(
            info_row,
            text="📋",
            font=("Segoe UI", 11),
            background="#1e1e1e",
            foreground="#0078d4"
        )
        version_icon.pack(side=tk.LEFT, padx=(0, 3))
        version_label = ttk.Label(
            info_row,
            text="Beta 1.0.0.1",
            font=("Segoe UI", 9),
            background="#1e1e1e",
            foreground="#ffffff"
        )
        version_label.pack(side=tk.LEFT, padx=(0, 10))
        author_icon = ttk.Label(
            info_row,
            text="👨‍💻",
            font=("Segoe UI", 11),
            background="#1e1e1e",
            foreground="#0078d4"
        )
        author_icon.pack(side=tk.LEFT, padx=(0, 3))
        author_label = ttk.Label(
            info_row,
            text="CavemanTechandGamming",
            font=("Segoe UI", 9),
            background="#1e1e1e",
            foreground="#ffffff"
        )
        author_label.pack(side=tk.LEFT, padx=(0, 10))
        license_icon = ttk.Label(
            info_row,
            text="📄",
            font=("Segoe UI", 11),
            background="#1e1e1e",
            foreground="#0078d4"
        )
        license_icon.pack(side=tk.LEFT, padx=(0, 3))
        license_label = ttk.Label(
            info_row,
            text="MIT",
            font=("Segoe UI", 9),
            background="#1e1e1e",
            foreground="#ffffff"
        )
        license_label.pack(side=tk.LEFT)

        # Support & Updates Section (condensed)
        support_frame = ttk.Frame(main_container)
        support_frame.pack(pady=(5, 5))
        support_title = ttk.Label(
            support_frame,
            text="Support & Updates",
            font=("Segoe UI", 11, "bold"),
            background="#1e1e1e",
            foreground="#ffffff"
        )
        support_title.pack(anchor=tk.W, pady=(0, 2))
        github_link_frame = ttk.Frame(support_frame)
        github_link_frame.pack()
        github_icon = ttk.Label(
            github_link_frame,
            text="🔗",
            font=("Segoe UI", 10),
            background="#1e1e1e",
            foreground="#0078d4"
        )
        github_icon.pack(side=tk.LEFT, padx=(0, 3))
        github_url_label = ttk.Label(
            github_link_frame,
            text="github.com/CavemanTechandGamming/Mainstall",
            font=("Segoe UI", 9),
            background="#1e1e1e",
            foreground="#888888"
        )
        github_url_label.pack(side=tk.LEFT)
        github_button = ttk.Button(
            support_frame,
            text="Open GitHub Repository",
            command=self.open_github_repository,
            style='TButton',
            width=24
        )
        github_button.pack(pady=(4, 0))

        # Copyright (smaller, less padding)
        copyright_frame = ttk.Frame(main_container)
        copyright_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 0))
        separator = tk.Canvas(copyright_frame, height=1, bg="#404040", highlightthickness=0)
        separator.pack(fill=tk.X, pady=(0, 6))
        copyright_label = ttk.Label(
            copyright_frame,
            text="© 2024 CavemanTechandGamming. All rights reserved.",
            font=("Segoe UI", 8),
            background="#1e1e1e",
            foreground="#888888"
        )
        copyright_label.pack()

    def initialize_system_settings_states(self):
        """
        Initialize all system settings states when the tab is first accessed.
        Reads current registry values and updates toggle switches accordingly.
        """
        print("Initializing System Settings states...")
        for setting_name, var in self.settings_vars.items():
            # Find the setting definition
            for setting in self.system_settings_definitions:
                if setting["name"] == setting_name:
                    self.initialize_setting_state(setting, var)
                    break

    def run_powershell_command(self, command: str, skip_security_check=False, visible_window=True):
        """
        Run a PowerShell command, optionally in a visible window.
        - Validates command for security
        - Shows error dialogs for invalid or dangerous commands
        - Runs command in a new PowerShell window if visible_window is True
        """
        print(f"Attempting to execute command: {command}")
        
        # Input validation
        if not command or len(command.strip()) == 0:
            messagebox.showerror("Error", "No command provided.")
            return
        
        if not skip_security_check:
            # Basic command injection prevention for user-supplied input
            dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '{', '}', '[', ']']
            if any(char in command for char in dangerous_chars):
                messagebox.showerror("Security Error", "Command contains potentially dangerous characters.")
                return
        
        # Validate command starts with expected patterns
        allowed_commands = [
            'winget install',
            'winget upgrade',
            'sfc /scannow',
            'dism /online',
            'chkdsk',
            'dism.exe /online',
            'cleanmgr',
            'remove-item',
            'write-host',
            'read-host',
            'ipconfig /flushdns',
            'stop-process',
            'wsreset.exe',
            'get-process',
            'cmd /c',
            'net stop',
            'net start',
            'ren ',
            'get-appxpackage',
            'reset-appxpackage',
            'add-appxpackage',
            'get-netadapter',
            'restart-netadapter',
            'get-itemproperty',
            'set-itemproperty',
            'reg query',
            'reg add',
            'checkpoint-computer',
            'netsh winsock reset',
            'netsh int ip reset',
            'wevtutil el',
            'wevtutil cl',
            'msdt.exe /id',
            'get-computerinfo',
            'out-file',
            'taskkill /f /im',
            'start explorer.exe'
        ]
        
        command_lower = command.lower()
        if not any(cmd in command_lower for cmd in allowed_commands):
            messagebox.showerror("Security Error", "Command not in allowed list.")
            return
        
        try:
            print(f"Executing PowerShell command: {command}")
            powershell_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
            if visible_window:
                subprocess.Popen([
                    powershell_path, 
                    "-NoExit", 
                    "-Command", 
                    command
                ], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.run([
                    powershell_path,
                    "-Command",
                    command
                ], capture_output=True, text=True, shell=True)
            print("PowerShell command executed successfully")
        except Exception as e:
            print(f"Error executing command: {e}")
            with open("mainstall_error.log", "a") as f:
                f.write(f"Error executing command: {e}\nCommand: {command}\n")
            messagebox.showerror("Error", f"Failed to execute command: {str(e)}\n\nCommand: {command}")
            
    def run_deep_disk_cleanup(self):
        """
        Run deep disk cleanup commands in sequence with security validation.
        Combines DISM, Disk Cleanup, and temp file removal.
        """
        commands = [
            "Dism.exe /Online /Cleanup-Image /StartComponentCleanup /ResetBase",
            "cleanmgr /verylowdisk /d C:",
            "Remove-Item \"$env:TEMP\\*\" -Recurse -Force -ErrorAction SilentlyContinue"
        ]
        
        # Validate each command before execution
        for cmd in commands:
            if not self._validate_command(cmd):
                messagebox.showerror("Security Error", f"Invalid command detected: {cmd}")
                return
        
        # Combine commands with semicolons for sequential execution
        combined_command = "; ".join(commands)
        self.run_powershell_command(combined_command)
        
    def _validate_command(self, command: str) -> bool:
        """
        Validate command for security purposes.
        Checks for dangerous characters and allowed command patterns.
        """
        if not command or len(command.strip()) == 0:
            return False
        
        # Check for dangerous characters
        dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '{', '}', '[', ']']
        if any(char in command for char in dangerous_chars):
            return False
        
        # Validate command starts with expected patterns
        allowed_commands = [
            'winget install',
            'winget upgrade',
            'sfc /scannow',
            'dism /online',
            'chkdsk',
            'dism.exe /online',
            'cleanmgr',
            'remove-item',
            'write-host',
            'read-host',
            'ipconfig /flushdns',
            'stop-process',
            'wsreset.exe',
            'get-process',
            'cmd /c',
            'net stop',
            'net start',
            'ren ',
            'get-appxpackage',
            'reset-appxpackage',
            'add-appxpackage',
            'get-netadapter',
            'restart-netadapter',
            'get-itemproperty',
            'set-itemproperty',
            'reg query',
            'reg add',
            'checkpoint-computer',
            'netsh winsock reset',
            'netsh int ip reset',
            'wevtutil el',
            'wevtutil cl',
            'msdt.exe /id',
            'get-computerinfo',
            'out-file',
            'taskkill /f /im',
            'start explorer.exe'
        ]
        
        command_lower = command.lower()
        return any(cmd in command_lower for cmd in allowed_commands)
        
    def install_software(self, app_name: str, app_id: str):
        """
        Install software using winget with confirmation and security validation.
        - Validates app_id format
        - Shows confirmation dialog
        - Runs install command in PowerShell
        """
        # Input validation and sanitization
        if not app_name or not app_id:
            messagebox.showerror("Error", "Invalid software parameters provided.")
            return
        
        # Sanitize inputs - only allow alphanumeric, dots, and hyphens
        import re
        if not re.match(r'^[a-zA-Z0-9.\-]+$', app_id):
            messagebox.showerror("Error", "Invalid software ID format.")
            return
        
        # Additional security check - validate app_id format
        if not app_id.count('.') >= 1:  # winget IDs should have at least one dot
            messagebox.showerror("Error", "Invalid winget ID format.")
            return
        
        result = messagebox.askyesno(
            "Confirm Installation",
            f"Do you want to install {app_name}?\n\n"
            f"Software ID: {app_id}\n"
            f"This will install the software silently in the background."
        )
        
        if result:
            try:
                # Use a more secure command construction
                command = f'winget install -e --id "{app_id}" --silent'
                self.run_powershell_command(command)
            except Exception as e:
                messagebox.showerror("Installation Error", 
                                   f"Failed to start installation of {app_name}:\n{str(e)}")
            
    def setup_universal_scrolling(self):
        """
        Set up mouse wheel scrolling that works everywhere in the application.
        Binds mouse wheel events recursively to all widgets and tabs.
        """
        def _on_mousewheel(event):
            # Find the active tab and scroll it
            current_tab = self.notebook.select()
            if current_tab:
                # Get the widget in the current tab
                tab_widget = self.notebook.nametowidget(current_tab)
                
                # Check if it's the installers tab (has canvas)
                for child in tab_widget.winfo_children():
                    if isinstance(child, tk.Canvas):
                        child.yview_scroll(int(-1*(event.delta/120)), "units")
                        break
                # Note: Maintenance tab doesn't need scrolling since it fits in the window
        
        # Bind mouse wheel to the root window and all its children recursively
        def bind_mousewheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        # Bind to the entire application
        bind_mousewheel_recursive(self.root)
        
        # Also bind to the notebook specifically
        self.notebook.bind("<MouseWheel>", _on_mousewheel)
        
        # Bind to the main window for maximum coverage
        self.root.bind("<MouseWheel>", _on_mousewheel)
        
        # Use event propagation to catch all mouse wheel events
        def propagate_mousewheel(event):
            _on_mousewheel(event)
            return "break"  # Prevent event from propagating further
        
        # Bind with propagation to catch all events
        self.root.bind_all("<MouseWheel>", propagate_mousewheel)
        
    def confirm_and_run_maintenance(self, task_name, command):
        """
        Show confirmation dialog and run a maintenance command if confirmed.
        """
        result = messagebox.askyesno(
            "Confirm Maintenance Task",
            f"Are you sure you want to run: {task_name}?\n\nThis will open a PowerShell window and make changes to your system.")
        if result:
            self.run_powershell_command(command, skip_security_check=True)

    def confirm_and_run_deep_disk_cleanup(self):
        """
        Show confirmation dialog and run deep disk cleanup if confirmed.
        """
        result = messagebox.askyesno(
            "Confirm Deep Disk Cleanup",
            "Are you sure you want to run Deep Disk Cleanup?\n\nThis will open a PowerShell window and perform advanced cleanup operations.")
        if result:
            self.run_deep_disk_cleanup()
        
    def confirm_and_run_quick_fix(self, task_name, command):
        """
        Show confirmation dialog and run a quick fix command if confirmed.
        """
        result = messagebox.askyesno(
            "Confirm Quick Fix",
            f"Are you sure you want to run: {task_name}?\n\nThis will open a PowerShell window and execute the command.")
        if result:
            self.run_powershell_command(command, skip_security_check=True)
            
    def get_registry_value(self, command):
        """
        Get a registry value using PowerShell.
        Returns the value as a string, or None if not found or error.
        """
        try:
            result = subprocess.run([
                "powershell.exe", 
                "-Command", 
                command
            ], capture_output=True, text=True, shell=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            else:
                return None
        except subprocess.TimeoutExpired:
            print(f"Timeout getting registry value for command: {command}")
            return None
        except Exception as e:
            print(f"Error getting registry value: {e}")
            return None
            
    def initialize_setting_state(self, setting, var):
        """
        Initialize the state of a setting toggle based on current system state.
        Reads registry and updates toggle/variable.
        """
        try:
            current_value = self.get_registry_value(setting["get_command"])
            print(f"Setting: {setting['name']}, Current value: '{current_value}'")
            toggle_widget = self.settings_widgets.get(setting["name"])
            
            if current_value is not None and current_value.strip():
                if current_value.strip() == setting["dark_value"]:
                    var.set(True)
                    if toggle_widget:
                        toggle_widget.set(True)
                    print(f"  -> Setting {setting['name']} to ON (value: {current_value})")
                else:
                    var.set(False)
                    if toggle_widget:
                        toggle_widget.set(False)
                    print(f"  -> Setting {setting['name']} to OFF (value: {current_value})")
            else:
                var.set(False)
                if toggle_widget:
                    toggle_widget.set(False)
                print(f"  -> Setting {setting['name']} to OFF (default, no value found)")
        except Exception as e:
            print(f"Error initializing setting {setting['name']}: {e}")
            var.set(False)
            toggle_widget = self.settings_widgets.get(setting["name"])
            if toggle_widget:
                toggle_widget.set(False)
            
    def toggle_setting(self, setting, var):
        """
        Toggle a system setting:
        - Sets registry value via PowerShell
        - Shows info dialog if reboot or logout is required
        - Handles errors and reverts toggle if needed
        """
        try:
            if var.get():
                new_value = setting["dark_value"]
                action = "enabled"
            else:
                new_value = setting["light_value"]
                action = "disabled"
            command = setting["set_command_template"].format(value=new_value)
            self.run_powershell_command(command, skip_security_check=True, visible_window=False)
            # Custom message for dark mode
            if setting["name"] == "Dark Mode for Apps":
                extra_msg = "\n\nYou may need to restart apps or log out and log back in for the change to take effect."
            elif setting["reboot_required"]:
                extra_msg = "\n\nA system restart may be required for changes to take effect."
            else:
                extra_msg = ""
            messagebox.showinfo(
                "Setting Updated",
                f"{setting['name']} has been {action}.{extra_msg}"
            )
        except Exception as e:
            print(f"Error toggling setting {setting['name']}: {e}")
            messagebox.showerror(
                "Error",
                f"Failed to update {setting['name']}: {str(e)}"
            )
            var.set(not var.get())
        
    def run(self):
        """
        Start the application main loop.
        """
        self.root.mainloop()

    def open_github_repository(self):
        """
        Open the GitHub repository in the default browser.
        """
        import webbrowser
        webbrowser.open("https://github.com/CavemanTechandGamming/Mainstall")

def main():
    """Main entry point of the application."""
    try:
        app = MainstallApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 