#!/usr/bin/env python3
"""
OSC to UDP Haptics Converter GUI
Converts OSC commands to SlimeVR UDP vibrate packets for VR full body tracking haptics.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import struct
import json
import os
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading


class HapticsOutput:
    """Represents a single haptics output configuration"""
    
    def __init__(self, output_id):
        self.output_id = output_id
        self.device_ip = tk.StringVar(value="127.0.0.1")
        self.device_port = tk.IntVar(value=6969)
        self.osc_path = tk.StringVar(value=f"/avatar/parameters/output{output_id}")
        self.packet_id = [0, 0, 0]  # 3-byte packet ID
        self.packet_number = 0
        
    def create_vibrate_packet(self, duration_ms):
        """
        Create a SlimeVR Vibrate packet
        
        Packet structure (14 bytes):
        - Bytes 0-2: Packet ID (uint8[3])
        - Byte 3: Packet Type (2 = Vibrate)
        - Bytes 4-11: Packet Number (uint64 BigEndian)
        - Bytes 12-13: Duration in milliseconds (uint16 BigEndian)
        """
        # Ensure duration is within valid range
        duration_ms = max(0, min(65535, int(duration_ms)))
        
        # Build packet
        packet = bytearray()
        
        # Packet ID (3 bytes)
        packet.extend(self.packet_id)
        
        # Packet Type (1 byte) - 2 for Vibrate
        packet.append(2)
        
        # Packet Number (8 bytes, BigEndian uint64)
        packet.extend(struct.pack('>Q', self.packet_number))
        self.packet_number += 1
        
        # Duration (2 bytes, BigEndian uint16)
        packet.extend(struct.pack('>H', duration_ms))
        
        return bytes(packet)
    
    def send_vibrate(self, duration_ms):
        """Send vibrate packet via UDP"""
        try:
            packet = self.create_vibrate_packet(duration_ms)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(packet, (self.device_ip.get(), self.device_port.get()))
            sock.close()
            return True
        except Exception as e:
            print(f"Error sending packet: {e}")
            return False
    
    def to_dict(self):
        """Convert to dictionary for saving"""
        return {
            'device_ip': self.device_ip.get(),
            'device_port': self.device_port.get(),
            'osc_path': self.osc_path.get(),
            'packet_id': self.packet_id
        }
    
    def from_dict(self, data):
        """Load from dictionary"""
        self.device_ip.set(data.get('device_ip', '127.0.0.1'))
        self.device_port.set(data.get('device_port', 6969))
        self.osc_path.set(data.get('osc_path', f'/avatar/parameters/output{self.output_id}'))
        self.packet_id = data.get('packet_id', [0, 0, 0])


class HapticsGUI:
    """Main GUI application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("OSC to UDP Haptics Converter")
        self.root.geometry("800x600")
        
        self.outputs = []
        self.osc_server = None
        self.osc_thread = None
        self.osc_port = tk.IntVar(value=9001)
        self.config_file = "haptics_config.json"
        
        self.setup_gui()
        self.load_config()
        
    def setup_gui(self):
        """Setup the GUI components"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="OSC to UDP Haptics Converter", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # OSC Server Settings
        server_frame = ttk.LabelFrame(main_frame, text="OSC Server Settings", padding="10")
        server_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(server_frame, text="OSC Listen Port:").grid(row=0, column=0, sticky=tk.W)
        port_entry = ttk.Entry(server_frame, textvariable=self.osc_port, width=10)
        port_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        self.server_status_label = ttk.Label(server_frame, text="Status: Stopped", 
                                            foreground="red")
        self.server_status_label.grid(row=0, column=2, padx=20)
        
        self.start_button = ttk.Button(server_frame, text="Start OSC Server", 
                                       command=self.toggle_osc_server)
        self.start_button.grid(row=0, column=3, padx=5)
        
        # Outputs container with scrollbar
        outputs_frame = ttk.LabelFrame(main_frame, text="Haptics Outputs", padding="10")
        outputs_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(2, weight=1)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(outputs_frame)
        scrollbar = ttk.Scrollbar(outputs_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        outputs_frame.columnconfigure(0, weight=1)
        outputs_frame.rowconfigure(0, weight=1)
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Add Output", 
                  command=self.add_output).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Save Config", 
                  command=self.save_config).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Load Config", 
                  command=self.load_config).grid(row=0, column=2, padx=5)
        
        # Add initial outputs
        for i in range(2):
            self.add_output()
    
    def create_output_frame(self, output, row_index):
        """Create GUI frame for an output"""
        output_frame = ttk.LabelFrame(self.scrollable_frame, 
                                      text=f"Output {output.output_id}", padding="10")
        output_frame.grid(row=row_index, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Device IP
        ttk.Label(output_frame, text="Device IP:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(output_frame, textvariable=output.device_ip, width=20).grid(
            row=0, column=1, sticky=tk.W, padx=5)
        
        # Device Port
        ttk.Label(output_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        ttk.Entry(output_frame, textvariable=output.device_port, width=10).grid(
            row=0, column=3, sticky=tk.W, padx=5)
        
        # OSC Path
        ttk.Label(output_frame, text="OSC Path:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(output_frame, textvariable=output.osc_path, width=40).grid(
            row=1, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # Test buttons
        ttk.Button(output_frame, text="Test (100ms)", 
                  command=lambda o=output: self.test_output(o, 100)).grid(
            row=2, column=0, padx=5, pady=5)
        ttk.Button(output_frame, text="Test (500ms)", 
                  command=lambda o=output: self.test_output(o, 500)).grid(
            row=2, column=1, padx=5, pady=5)
        ttk.Button(output_frame, text="Test (1000ms)", 
                  command=lambda o=output: self.test_output(o, 1000)).grid(
            row=2, column=2, padx=5, pady=5)
        ttk.Button(output_frame, text="Remove", 
                  command=lambda o=output, f=output_frame: self.remove_output(o, f),
                  style='Danger.TButton').grid(
            row=2, column=3, padx=5, pady=5)
        
        return output_frame
    
    def add_output(self):
        """Add a new haptics output"""
        output_id = len(self.outputs)
        output = HapticsOutput(output_id)
        self.outputs.append(output)
        
        # Create GUI frame for this output
        self.create_output_frame(output, output_id)
    
    def remove_output(self, output, frame):
        """Remove an output"""
        if len(self.outputs) <= 1:
            messagebox.showwarning("Warning", "You must have at least one output")
            return
        
        # Remove the output from the list
        if output in self.outputs:
            self.outputs.remove(output)
        
        # Destroy the GUI frame
        frame.destroy()
    
    def test_output(self, output, duration_ms):
        """Test an output by sending a vibrate packet"""
        if output.send_vibrate(duration_ms):
            messagebox.showinfo("Success", 
                              f"Sent {duration_ms}ms vibrate packet to {output.device_ip.get()}:{output.device_port.get()}")
        else:
            messagebox.showerror("Error", "Failed to send vibrate packet")
    
    def toggle_osc_server(self):
        """Start or stop the OSC server"""
        if self.osc_server is None:
            self.start_osc_server()
        else:
            self.stop_osc_server()
    
    def start_osc_server(self):
        """Start the OSC server"""
        try:
            # Create dispatcher
            dispatcher = Dispatcher()
            
            # Add handlers for each output
            for output in self.outputs:
                path = output.osc_path.get()
                dispatcher.map(path, self.osc_handler, output)
            
            # Create and start server
            self.osc_server = BlockingOSCUDPServer(
                ("0.0.0.0", self.osc_port.get()), dispatcher)
            
            # Run server in thread
            self.osc_thread = threading.Thread(target=self.osc_server.serve_forever, 
                                              daemon=True)
            self.osc_thread.start()
            
            self.server_status_label.config(text="Status: Running", foreground="green")
            self.start_button.config(text="Stop OSC Server")
            print(f"OSC Server started on port {self.osc_port.get()}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start OSC server: {e}")
    
    def stop_osc_server(self):
        """Stop the OSC server"""
        if self.osc_server:
            self.osc_server.shutdown()
            self.osc_server = None
            self.osc_thread = None
            self.server_status_label.config(text="Status: Stopped", foreground="red")
            self.start_button.config(text="Start OSC Server")
            print("OSC Server stopped")
    
    def osc_handler(self, address, output, *args):
        """Handle incoming OSC messages"""
        print(f"Received OSC message: {address} - args: {args}")
        
        # Determine duration from OSC value
        # If value is a boolean/float, map it to duration
        if args:
            value = args[0]
            if isinstance(value, bool):
                duration_ms = 100 if value else 0
            elif isinstance(value, (int, float)):
                # Map 0-1 range to 0-500ms, or use direct value if > 1
                if 0 <= value <= 1:
                    duration_ms = int(value * 500)
                else:
                    duration_ms = int(value)
            else:
                duration_ms = 100  # Default
        else:
            duration_ms = 100  # Default if no args
        
        # Send vibrate packet
        output.send_vibrate(duration_ms)
    
    def save_config(self):
        """Save configuration to file"""
        config = {
            'osc_port': self.osc_port.get(),
            'outputs': [output.to_dict() for output in self.outputs]
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Success", "Configuration saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
    
    def load_config(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Load OSC port
            self.osc_port.set(config.get('osc_port', 9001))
            
            # Clear existing outputs
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.outputs.clear()
            
            # Load outputs
            outputs_data = config.get('outputs', [])
            if outputs_data:
                for i, output_data in enumerate(outputs_data):
                    output = HapticsOutput(i)
                    output.from_dict(output_data)
                    self.outputs.append(output)
                    
                    # Create GUI for output using helper method
                    self.create_output_frame(output, i)
            
            print("Configuration loaded")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_osc_server()
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = HapticsGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
