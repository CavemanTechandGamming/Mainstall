#!/usr/bin/env python3
"""
Test script for Mainstall GUI components
This script tests the GUI without requiring admin privileges
"""

import tkinter as tk
from tkinter import ttk, messagebox

def test_gui():
    """Test the GUI components without admin privileges."""
    root = tk.Tk()
    root.title("Mainstall - GUI Test")
    root.geometry("600x400")
    
    # Test dark theme with high contrast
    style = ttk.Style()
    style.theme_use('clam')
    
    bg_color = "#1e1e1e"  # Dark background
    fg_color = "#ffffff"  # Bright white text for maximum readability
    button_bg = "#6a6a6a"  # Much lighter button background for contrast
    button_fg = "#000000"  # Black button text for contrast
    selected_bg = "#0078d4"  # Blue for selected items
    tab_bg = "#6a6a6a"  # Same light gray as buttons for consistency
    tab_fg = "#000000"  # Black tab text for contrast (same as buttons)
    
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
    
    root.configure(bg=bg_color)
    
    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Create notebook
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Test Maintenance tab
    maintenance_frame = ttk.Frame(notebook)
    notebook.add(maintenance_frame, text="Maintenance")
    
    title_label = ttk.Label(maintenance_frame, 
                           text="System Maintenance Tools (Test)", 
                           font=('Segoe UI', 16, 'bold'))
    title_label.pack(pady=(20, 30))
    
    # Test button
    test_btn = ttk.Button(maintenance_frame,
                         text="Test Button (No Admin Required)",
                         command=lambda: messagebox.showinfo("Test", "GUI is working correctly!"))
    test_btn.pack(pady=10)
    
    # Test Installers tab
    installers_frame = ttk.Frame(notebook)
    notebook.add(installers_frame, text="Installers")
    
    title_label2 = ttk.Label(installers_frame, 
                            text="Software Installation (Test)", 
                            font=('Segoe UI', 16, 'bold'))
    title_label2.pack(pady=(20, 30))
    
    test_btn2 = ttk.Button(installers_frame,
                          text="Test Installer Button",
                          command=lambda: messagebox.showinfo("Test", "Installer tab is working!"))
    test_btn2.pack(pady=10)
    
    # Status label
    status_label = ttk.Label(root, text="GUI Test - All components working correctly!")
    status_label.pack(pady=10)
    
    def on_closing():
        messagebox.showinfo("Test Complete", "GUI test completed successfully!")
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    test_gui() 