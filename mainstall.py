#!/usr/bin/env python3
"""
Mainstall - Windows System Maintenance and Software Installation Tool
A professional-grade desktop application for Windows system maintenance and software installation.

Author: Mainstall
License: MIT
"""

import sys
import os
import ctypes
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import List, Tuple

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
    """Main application class for Mainstall."""
    
    def __init__(self):
        """Initialize the Mainstall application."""
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
        """Setup the main window with proper styling and configuration."""
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
        """Configure dark theme styles with high contrast."""
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
        """Create and organize all GUI widgets."""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_maintenance_tab()
        self.create_installers_tab()
        self.create_about_tab()
        
    def create_maintenance_tab(self):
        """Create the Maintenance tab with all maintenance buttons."""
        maintenance_frame = ttk.Frame(self.notebook)
        self.notebook.add(maintenance_frame, text="Maintenance")
        
        # Title
        title_label = ttk.Label(maintenance_frame, 
                               text="System Maintenance Tools", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(20, 30))
        
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
            ("Winget Upgrade All", "winget upgrade --all", "Update all installed winget packages to their latest versions"),
            ("SFC Scan (System File Checker)", "sfc /scannow", "Scan and repair corrupted Windows system files"),
            ("DISM ScanHealth", "DISM /Online /Cleanup-Image /ScanHealth", "Scan Windows image for component store corruption"),
            ("DISM CheckHealth", "DISM /Online /Cleanup-Image /CheckHealth", "Check Windows image for component store corruption"),
            ("DISM RestoreHealth", "DISM /Online /Cleanup-Image /RestoreHealth", "Repair Windows image component store corruption"),
            ("Check Disk (C:)", "chkdsk C:", "Check and repair disk errors on C: drive"),
            ("Deep Disk Cleanup", None, "Perform comprehensive disk cleanup including DISM, Disk Cleanup, and temp files"),  # Special case
        ]
        
        # Create tooltip function
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
        
        # Distribute buttons between columns
        for i, (text, command, tooltip_text) in enumerate(maintenance_buttons):
            if text == "Deep Disk Cleanup":
                # Place Deep Disk Cleanup in the right column
                btn = ttk.Button(right_column,
                               text=text,
                               command=self.confirm_and_run_deep_disk_cleanup,
                               style='TButton',
                               width=25)
                btn.pack(fill=tk.X, pady=5)
                create_tooltip(btn, tooltip_text)
            else:
                # Place other buttons alternating between columns
                target_column = left_column if i % 2 == 0 else right_column
                btn = ttk.Button(target_column, 
                               text=text,
                               command=lambda t=text, c=command: self.confirm_and_run_maintenance(t, c),
                               style='TButton',
                               width=25)
                btn.pack(fill=tk.X, pady=5)
                create_tooltip(btn, tooltip_text)
        
        # Add some spacing before the Run All button
        spacer = ttk.Frame(maintenance_frame, height=20)
        spacer.pack(fill=tk.X)
        
        # Run All Maintenance button centered at bottom
        run_all_btn = ttk.Button(maintenance_frame,
                               text="Run All Maintenance",
                               command=self.run_all_maintenance,
                               style='TButton',
                               width=25)
        run_all_btn.pack(pady=20)
        create_tooltip(run_all_btn, "Execute all maintenance tasks in sequence: Winget upgrade, SFC scan, DISM checks, disk check, and cleanup")
        
    def create_installers_tab(self):
        """Create the Installers tab with all software installation buttons."""
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
        
        # Title (now inside scrollable_frame, with dark background)
        title_label = ttk.Label(scrollable_frame, 
                               text="Software Installation", 
                               font=('Segoe UI', 16, 'bold'),
                               background="#1e1e1e", foreground="#ffffff")
        title_label.pack(pady=(20, 30))
        
        # Software categories (alphabetically sorted)
        software_categories = {
            "Browsers & Communication": [
                ("Discord", "Discord.Discord"),
                ("Google Chrome", "Google.Chrome"),
                ("Mozilla Firefox", "Mozilla.Firefox"),
            ],
            "Development Tools": [
                ("Atom", "GitHub.Atom"),
                ("Docker Desktop", "Docker.DockerDesktop"),
                ("Git for Windows", "Git.Git"),
                ("Node.js", "OpenJS.NodeJS"),
                ("Postman", "Postman.Postman"),
                ("Python", "Python.Python.3.12"),
                ("Sublime Text", "SublimeHQ.SublimeText.4"),
                ("Visual Studio Code", "Microsoft.VisualStudioCode"),
                ("WinMerge", "WinMerge.WinMerge"),
            ],
            "File Management": [
                ("7-Zip", "7zip.7zip"),
                ("Everything", "voidtools.Everything"),
                ("FileZilla", "FileZilla.FileZilla"),
                ("FreeFileSync", "FreeFileSync.FreeFileSync"),
                ("Rufus", "Rufus.Rufus"),
                ("TeraCopy", "CodeSector.TeraCopy"),
                ("WinRAR", "RARLab.WinRAR"),
                ("WinSCP", "WinSCP.WinSCP"),
            ],
            "Gaming & Entertainment": [
                ("Battle.net", "Blizzard.BattleNet"),
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
                ("AutoHotkey", "AutoHotkey.AutoHotkey"),
                ("Calibre", "calibre.calibre"),
                ("Greenshot", "Greenshot.Greenshot"),
                ("KeePass", "KeePassXCTeam.KeePassXC"),
                ("LibreOffice", "TheDocumentFoundation.LibreOffice"),
                ("Microsoft PowerToys", "Microsoft.PowerToys"),
                ("Notepad++", "Notepad++.Notepad++"),
                ("Obsidian", "Obsidian.Obsidian"),
                ("ShareX", "ShareX.ShareX"),
                ("Sumatra PDF", "SumatraPDF.SumatraPDF"),
                ("Trello", "Atlassian.Trello"),
                ("Typora", "Typora.Typora"),
            ],
            "Security": [
                ("Avast Free Antivirus", "AvastSoftware.AvastFreeAntivirus"),
                ("AVG AntiVirus Free", "AVGSoftware.AVG"),
                ("Bitdefender Free", "Bitdefender.Bitdefender"),
                ("Bitwarden", "Bitwarden.Bitwarden"),
                ("CCleaner", "Piriform.CCleaner"),
                ("DefenderUI", "DefenderUI.DefenderUI"),
                ("GlassWire", "SecureMixLLC.GlassWire"),
                ("Malwarebytes", "Malwarebytes.Malwarebytes"),
                ("Spybot Search & Destroy", "SaferNetworkingLtd.SpybotSearchAndDestroy"),
                ("VeraCrypt", "IDRIX.VeraCrypt"),
                ("Windows Defender Exclusions Manager", "Microsoft.WindowsDefenderExclusionsManager"),
                ("Windows Firewall Control", "BiniSoft.WindowsFirewallControl"),
            ],
            "System Monitoring & Diagnostics": [
                ("AIDA64", "FinalWire.AIDA64"),
                ("Autoruns", "Microsoft.Autoruns"),
                ("CrystalDiskInfo", "CrystalDewWorld.CrystalDiskInfo"),
                ("CPU-Z", "CPUID.CPU-Z"),
                ("FurMark", "Geeks3D.FurMark"),
                ("HWiNFO", "REALiX.HWiNFO"),
                ("MemTest86", "PassMark.MemTest86"),
                ("Prime95", "Mersenne.Prime95"),
                ("Process Explorer", "Microsoft.ProcessExplorer"),
                ("Process Hacker", "ProcessHacker.ProcessHacker"),
                ("Process Monitor", "Microsoft.ProcessMonitor"),
                ("Revo Registry Cleaner", "VS Revo Group.Revo Registry Cleaner"),
                ("Revo Uninstaller", "VS Revo Group.Revo Uninstaller"),
                ("TCPView", "Microsoft.TCPView"),
                ("WinDirStat", "WinDirStat.WinDirStat"),
            ],
        }
        
        # Create category sections in alphabetical order
        for category_name in sorted(software_categories.keys()):
            software_list = software_categories[category_name]
            
            # Category header (centered)
            category_label = ttk.Label(scrollable_frame, 
                                     text=category_name, 
                                     font=('Segoe UI', 12, 'bold'))
            category_label.pack(expand=True, padx=20, pady=(15, 5))  # Center the label
            
            # Create centered container for the category
            category_container = ttk.Frame(scrollable_frame)
            category_container.pack(fill=tk.X, padx=20, pady=(0, 10))
            
            # Create inner frame for centering the columns
            inner_frame = ttk.Frame(category_container)
            inner_frame.pack(expand=True)  # Center the inner frame
            
            # Create two columns for this category
            left_column = ttk.Frame(inner_frame)
            right_column = ttk.Frame(inner_frame)
            
            left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
            
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
                # Browsers & Communication
                "Discord": "Voice, video, and text communication platform designed for gamers and communities. Features include server creation, voice channels, screen sharing, file sharing, and integration with gaming platforms. Perfect for team communication, community building, and remote collaboration.",
                "Google Chrome": "Fast, secure web browser with extensive extension support and Google integration. Features include automatic updates, built-in security, incognito mode, cross-device sync, and powerful developer tools. The most popular browser worldwide with excellent performance and compatibility.",
                "Mozilla Firefox": "Privacy-focused web browser with customizable features and strong security. Includes tracking protection, enhanced privacy controls, customizable interface, extensive add-on ecosystem, and open-source transparency. Excellent for users who prioritize privacy and customization.",
                
                # Development Tools
                "Git for Windows": "Distributed version control system for tracking code changes and collaboration. Features include branching, merging, conflict resolution, remote repository management, and integration with development platforms. Essential for software development, code management, and team collaboration.",
                "Python": "High-level programming language known for simplicity and versatility. Used for web development, data analysis, automation, AI/ML, scientific computing, and scripting. Features extensive libraries, cross-platform compatibility, and beginner-friendly syntax. Perfect for both beginners and advanced developers.",
                "Visual Studio Code": "Lightweight but powerful source code editor with extensive extension support. Features include IntelliSense, debugging, Git integration, terminal, customizable themes, and support for hundreds of programming languages. Popular among developers for its speed and extensibility.",
                "WinMerge": "Professional file comparison and merge tool for developers and IT professionals. Features include side-by-side file comparison, three-way merge, syntax highlighting for code files, folder comparison, and advanced merge conflict resolution. Essential for code reviews, version control operations, and detecting differences between files. Supports multiple file formats and integrates with version control systems.",
                
                # File Management
                "7-Zip": "High-compression file archiver with strong AES-256 encryption. Supports multiple formats (7z, ZIP, RAR, TAR, etc.), creates self-extracting archives, and offers excellent compression ratios. Free, open-source, and widely trusted for secure file compression and archiving.",
                "FileZilla": "Cross-platform FTP client for secure file transfers between local and remote servers. Supports FTP, FTPS, and SFTP protocols with drag-and-drop interface, site manager, and transfer queue. Essential for web developers and system administrators managing remote files.",
                "Rufus": "Lightweight utility for creating bootable USB drives from ISO files. Supports UEFI and legacy boot modes, various file systems, and can format drives. Essential for system administrators, IT professionals, and anyone needing to create bootable media for system recovery or installation.",
                "TeraCopy": "Fast and reliable file copying utility with verification and error recovery. Features include pause/resume transfers, error recovery, file verification, integration with Windows Explorer, and detailed progress reporting. Significantly faster than Windows copy with better reliability.",
                "WinRAR": "Popular file compression and archiving utility with strong encryption. Supports multiple formats, creates self-extracting archives, password protection, and repair capabilities. Widely used for file compression, backup creation, and secure file sharing.",
                
                # Graphics & Media
                "Audacity": "Free, open-source audio recording and editing software with professional features. Includes multi-track editing, effects, noise reduction, audio analysis, and support for various audio formats. Perfect for podcasting, music production, audio restoration, and educational use.",
                "Blender": "Professional 3D modeling, animation, and rendering software with comprehensive toolset. Features include modeling, sculpting, texturing, rigging, animation, rendering, video editing, and game development. Free alternative to expensive 3D software with active community support.",
                "GIMP": "Free image editing software similar to Photoshop with professional capabilities. Features include layers, masks, filters, brushes, scripting, and support for various file formats. Excellent for photo editing, graphic design, digital art, and web graphics creation.",
                "HandBrake": "Video transcoder for converting video between different formats and codecs. Features include batch processing, quality presets, subtitle support, chapter markers, and hardware acceleration. Essential for video conversion, compression, and format compatibility.",
                "Inkscape": "Professional vector graphics editor for creating scalable illustrations and designs. Features include path editing, text tools, gradients, filters, and support for SVG format. Perfect for logo design, illustrations, technical drawings, and web graphics.",
                "IrfanView": "Fast and lightweight image viewer and editor with extensive format support. Features include batch processing, slideshow creation, basic editing tools, and plugin support. Excellent for quick image viewing, basic editing, and format conversion.",
                "K-Lite Codec Pack": "Comprehensive collection of audio and video codecs for media playback. Includes codecs for various formats, media players, and tools for codec management. Essential for playing various media formats and ensuring compatibility across different file types.",
                "OBS Studio": "Free streaming and recording software with professional broadcasting features. Includes scene composition, real-time video/audio capture, streaming to multiple platforms, and extensive plugin support. Perfect for content creators, streamers, and video production.",
                "Paint.NET": "Image and photo editing software with layers, effects, and user-friendly interface. Features include layer support, effects, adjustments, and plugin system. Excellent alternative to Photoshop for basic to intermediate image editing needs.",
                "VLC Media Player": "Versatile media player supporting virtually all audio and video formats. Features include streaming, subtitle support, audio/video filters, and cross-platform compatibility. Most reliable media player for playing any type of media file without codec issues.",
                
                # Network & Remote Access
                "Advanced IP Scanner": "Network scanner to discover devices and analyze network infrastructure. Features include device detection, port scanning, shared folder access, remote shutdown, and network monitoring. Essential for network administrators and IT professionals managing network security.",
                "AnyDesk": "Remote desktop software for secure remote access and support. Features include file transfer, remote printing, session recording, and cross-platform compatibility. Popular for remote IT support, telecommuting, and accessing computers from anywhere.",
                "LocalSend": "Secure and private file sharing application for local networks. Features include end-to-end encryption, no server required, cross-platform support, and simple drag-and-drop interface. Perfect for secure file sharing between devices on the same network.",
                "PuTTY": "SSH and telnet client for secure remote connections to servers and network devices. Features include session management, key authentication, port forwarding, and terminal customization. Essential for system administrators and developers working with remote servers.",
                "TeamViewer": "Remote control and file transfer software with enterprise-grade security. Features include unattended access, file transfer, remote printing, and cross-platform support. Widely used for remote IT support, collaboration, and accessing computers remotely.",
                "Wireshark": "Network protocol analyzer for troubleshooting and analyzing network traffic. Features include packet capture, protocol analysis, filtering, and detailed packet inspection. Essential tool for network administrators, security professionals, and developers debugging network issues.",
                
                # Office & Productivity
                "Adobe Acrobat Reader": "PDF viewer and document management with advanced features. Includes form filling, digital signatures, commenting tools, and integration with Adobe services. Industry standard for viewing, printing, and interacting with PDF documents.",
                "AutoHotkey": "Automation scripting language for Windows with powerful automation capabilities. Features include hotkey creation, macro recording, GUI automation, and custom scripting. Perfect for automating repetitive tasks, creating shortcuts, and improving productivity.",
                "Greenshot": "Screenshot and image editing tool with annotation capabilities. Features include region capture, window capture, scrolling capture, annotation tools, and integration with various applications. Excellent for documentation, tutorials, and visual communication.",
                "KeePass": "Secure password manager with strong encryption and local storage. Features include password generation, secure notes, file attachments, and plugin support. Perfect for managing passwords securely without relying on cloud services.",
                "LibreOffice": "Free office suite with word processor, spreadsheet, presentation, and database applications. Features include Microsoft Office compatibility, extensive formatting options, and cross-platform support. Excellent free alternative to Microsoft Office.",
                "Microsoft PowerToys": "Collection of utilities for power users to enhance Windows productivity. Features include FancyZones for window management, PowerRename for batch file renaming, PowerToys Run for quick app launching, and various other productivity tools.",
                "Notepad++": "Advanced text editor with syntax highlighting and extensive plugin support. Features include multi-document editing, search and replace, macro recording, and support for hundreds of programming languages. Essential for developers and power users.",
                "ShareX": "Screen capture and file sharing utility with extensive customization options. Features include region capture, scrolling capture, video recording, OCR, and integration with various sharing services. Perfect for content creators and documentation.",
                
                # Security
                "Avast Free Antivirus": "Comprehensive antivirus protection with real-time scanning and threat detection. Features include behavioral analysis, web protection, email scanning, and network security. Popular free antivirus with strong protection capabilities.",
                "AVG AntiVirus Free": "Popular antivirus with file and web protection, plus performance optimization. Features include real-time protection, web browsing protection, file shredder, and performance scanning. Reliable free antivirus with good detection rates.",
                "Bitdefender Free": "Advanced antivirus with behavioral detection and minimal system impact. Features include real-time protection, phishing protection, and cloud-based threat detection. Known for excellent protection with low resource usage.",
                "CCleaner": "System optimization and privacy protection tool with registry cleaning. Features include temporary file cleanup, registry optimization, startup management, and privacy protection. Essential for maintaining system performance and privacy.",
                "DefenderUI": "Enhanced interface for Windows Defender settings and configuration. Features include advanced settings access, real-time protection controls, and detailed security information. Perfect for users who want more control over Windows Defender.",
                "GlassWire": "Network monitoring and firewall visualization with security alerts. Features include network activity monitoring, bandwidth usage tracking, and security threat detection. Excellent for understanding network activity and detecting suspicious behavior.",
                "Malwarebytes": "Anti-malware software for threat detection and removal with real-time protection. Features include malware scanning, ransomware protection, and web protection. Specialized in detecting and removing advanced threats that traditional antivirus might miss.",
                "Spybot Search & Destroy": "Anti-spyware and registry protection with immunization features. Features include spyware detection, registry protection, and system immunization. Excellent for removing spyware and preventing future infections.",
                "Windows Defender Exclusions Manager": "Tool for managing Windows Defender exclusions and security settings. Features include easy exclusion management, security policy configuration, and detailed security information. Essential for IT professionals managing Windows security.",
                "Windows Firewall Control": "Enhanced Windows Firewall management with advanced configuration options. Features include rule management, network monitoring, and security policy enforcement. Perfect for advanced users who need more control over Windows Firewall.",
                
                # System Utilities
                "CPU-Z": "System information and hardware monitoring tool with detailed component analysis. Features include CPU information, memory details, motherboard specs, and real-time monitoring. Essential for system diagnostics, hardware verification, and performance analysis.",
                "HWiNFO": "Comprehensive hardware analysis and monitoring with detailed system information. Features include sensor monitoring, hardware detection, performance analysis, and reporting capabilities. Professional tool for detailed system analysis and monitoring.",
                "Revo Registry Cleaner": "Advanced registry cleaning and optimization with backup and restore features. Features include registry analysis, safe cleaning, backup creation, and detailed reporting. Essential for maintaining registry health and system performance.",
                "Revo Uninstaller": "Complete software removal with leftover cleanup and advanced uninstallation. Features include forced uninstallation, leftover detection, startup manager, and system optimization. Superior to Windows uninstaller for complete software removal.",
                "WinDirStat": "Disk usage statistics and cleanup tool with visual file analysis. Features include disk space analysis, file type breakdown, and cleanup recommendations. Essential for managing disk space and identifying large files.",
                
                # Gaming & Entertainment
                "Epic Games Launcher": "Digital distribution platform for games with free weekly games and exclusive titles. Features include game library management, social features, cloud saves, and regular free game offerings. Popular platform for PC gaming with competitive pricing.",
                "Steam": "Digital distribution platform for games and software with extensive community features. Features include game library, community forums, workshop content, cloud saves, and regular sales. The largest PC gaming platform with millions of users.",
                "Ubisoft Connect": "Digital distribution platform for Ubisoft games with social and competitive features. Features include game library, achievements, cloud saves, and cross-platform connectivity. Essential for playing Ubisoft games and accessing exclusive content.",
            }
            
            # Distribute buttons between columns with uniform sizing and tooltips
            for i, (app_name, app_id) in enumerate(software_list):
                btn = ttk.Button(
                    left_column if i % 2 == 0 else right_column,
                    text=app_name,  # Remove "Install" prefix
                    command=lambda name=app_name, id=app_id: self.install_software(name, id),
                    style='TButton',
                    width=35  # Make buttons wider
                )
                btn.pack(fill=tk.X, pady=2, padx=5)  # Add horizontal padding for consistency
                
                # Add tooltip for this software
                tooltip_text = software_tooltips.get(app_name, f"Install {app_name}")
                create_tooltip(btn, tooltip_text)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Ensure content starts at the top and update scroll region
        canvas.update_idletasks()
        canvas.yview_moveto(0)
        
    def create_about_tab(self):
        """Create the About tab with app information."""
        about_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(about_frame, text="About")

        about_label = ttk.Label(
            about_frame,
            text=(
                "Mainstall\n"
                "Professional Windows Maintenance & Software Installation Tool\n\n"
                "Version: Beta 1.0.0.0\n"
                "Author: CavemanTechandGamming\n"
                "License: MIT\n\n"
                "For support or updates, visit: https://github.com/CavemanTechandGamming/Mainstall"
            ),
            font=("Segoe UI", 12),
            background="#1e1e1e",
            foreground="#ffffff",
            justify="center",
            anchor="center"
        )
        about_label.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)
        
    def run_powershell_command(self, command: str, skip_security_check=False):
        """Run a PowerShell command in a new window with optional security validation."""
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
            'read-host'
        ]
        
        command_lower = command.lower()
        if not any(cmd in command_lower for cmd in allowed_commands):
            messagebox.showerror("Security Error", "Command not in allowed list.")
            return
        
        try:
            print(f"Executing PowerShell command: {command}")
            # Use full path to PowerShell and proper security measures
            powershell_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
            subprocess.Popen([
                powershell_path, 
                "-NoExit", 
                "-Command", 
                command
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
            print("PowerShell command executed successfully")
        except Exception as e:
            print(f"Error executing command: {e}")
            # Log error to a file for troubleshooting
            with open("mainstall_error.log", "a") as f:
                f.write(f"Error executing command: {e}\nCommand: {command}\n")
            messagebox.showerror("Error", f"Failed to execute command: {str(e)}\n\nCommand: {command}")
            
    def run_deep_disk_cleanup(self):
        """Run deep disk cleanup commands in sequence with security validation."""
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
        
    def run_all_maintenance(self):
        result = messagebox.askyesno(
            "Confirm Run All Maintenance",
            "Are you sure you want to run all maintenance tasks?\n\nThis will open multiple PowerShell windows and make changes to your system.")
        if not result:
            return
        commands = [
            "winget upgrade --all",
            "sfc /scannow",
            "DISM /Online /Cleanup-Image /CheckHealth",
            "DISM /Online /Cleanup-Image /ScanHealth",
            "DISM /Online /Cleanup-Image /RestoreHealth",
            "chkdsk C:",
            "Dism.exe /Online /Cleanup-Image /StartComponentCleanup /ResetBase; cleanmgr /verylowdisk /d C:; Remove-Item \"$env:TEMP\\*\" -Recurse -Force -ErrorAction SilentlyContinue"
        ]
        # Validate each command before execution
        for cmd in commands:
            if not self._validate_command(cmd):
                messagebox.showerror("Security Error", f"Invalid command detected: {cmd}")
                return
        # Combine all commands with semicolons for sequential execution
        combined_command = "; ".join(commands)
        self.run_powershell_command(combined_command, skip_security_check=True)
        
    def _validate_command(self, command: str) -> bool:
        """Validate command for security purposes."""
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
            'remove-item'
        ]
        
        command_lower = command.lower()
        return any(cmd in command_lower for cmd in allowed_commands)
        
    def install_software(self, app_name: str, app_id: str):
        """Install software using winget with confirmation and security validation."""
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
        """Set up mouse wheel scrolling that works everywhere in the application."""
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
        result = messagebox.askyesno(
            "Confirm Maintenance Task",
            f"Are you sure you want to run: {task_name}?\n\nThis will open a PowerShell window and make changes to your system.")
        if result:
            self.run_powershell_command(command, skip_security_check=True)

    def confirm_and_run_deep_disk_cleanup(self):
        result = messagebox.askyesno(
            "Confirm Deep Disk Cleanup",
            "Are you sure you want to run Deep Disk Cleanup?\n\nThis will open a PowerShell window and perform advanced cleanup operations.")
        if result:
            self.run_deep_disk_cleanup()
        
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()

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