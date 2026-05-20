import win32com.client  # For COM object interaction with SAP GUI
import pygetwindow as gw

import sys
import time
import subprocess
import os

from screeninfo import get_monitors


class SapModel:

    def __init__(self, username: str = None, password: str = None, attach_only=False):

        self.username = username
        self.password = password

        self.sap_path = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"

        if attach_only:
            self.sessions = self.attach_to_existing_sessions()
        else:
            self.restart_sap_gui_()
            self.sessions = self.generate_sessions_()
            
                
    # def generate_session(self):
    #     return self.session
    def get_sessions(self):
        return self.sessions

    def generate_sessions_(self, sap_system_name = 'ERP_Productivo', sap_client = '020', n_extra_sessions = 5): # Max 5 extras
        """
        Establishes a connection to SAP GUI.
        This function launches or connects to an existing SAP GUI session,
        opens a connection to the specified system, and logs in.
        
        Returns:
            session: The active SAP GUI session object if successful, None otherwise.
        """

        if n_extra_sessions > 5:
            print('⚠️  There could not be more than 6 sessions, 5 sessions were established...')
            n_extra_sessions = 5

        try:
            # Get the SAP GUI application object
            sap_gui_app = win32com.client.GetObject("SAPGUI")
            if not sap_gui_app:
                print("‼️  SAP GUI is not running. Starting it...\n")
                # If not running, you might need to launch it manually or via subprocess (not shown here for simplicity)
                sys.exit(1)
            
            # Get the scripting engine
            scripting_engine = sap_gui_app.GetScriptingEngine
            
            # Open a new connection or use existing
            connection = scripting_engine.OpenConnection(sap_system_name, True)  # True for synchronous
            
            # Get the first session (session 0)
            session = connection.Sessions(0)
            
            # Log in
            session.findById("").text = sap_client
            session.findById("").text = self.username
            session.findById("").text = self.password
            session.findById("").text = 'ES'
            session.findById("wnd[0]").sendVKey(0)  # Press Enter
            
            print("✅  Successfully connected and logged in to SAP.\n")
            # return session

            
            active_sessions = [session]

            # Get current number of sessions to know where the new ones start
            initial_count = connection.Sessions.Count 
            
            for _ in range(n_extra_sessions):
                # print(dir(connection), '\n')
                # print(inspect.getmembers(connection), '\n')
                session.CreateSession()
                # Brief pause to allow SAP to initialize the window
                time.sleep(1) 
            
            # Capture the newly created session objects
            # Note: connection.Sessions is a collection starting from index 0
            for i in range(initial_count, connection.Sessions.Count):
                active_sessions.append(connection.Sessions(i))

            print("✅  Multiple session created succesfully.\n")
                
            return active_sessions
        
        except Exception as e:
            print(f"‼️  Error generating sessions in SAP: {e}\n")
            return None
        
    def unmarshal_session(self, session_stream_by_interface):
        return win32com.client.Dispatch(session_stream_by_interface)
    
    def restart_sap_gui_(self):
        """
        Restarts SAP GUI: Closes it if open, then launches it again.
        """
        if self.is_sap_gui_open():
            self.close_sap_gui()
        self.launch_sap_gui()
        print("✅ SAP GUI restarted successfully.\n")

    def close_sap_gui(self):
        """
        Closes SAP GUI by forcefully terminating the saplogon.exe process.
        Uses taskkill for simplicity (Windows-specific).
        Alternative: Use psutil for more controlled process management.
        """
        try:
            os.system('taskkill /IM saplogon.exe /F')
            time.sleep(2)  # Wait for process to terminate
            print("🔁 SAP GUI closed successfully.\n")
        except Exception as e:
            print(f"‼️  Error closing SAP GUI: {e}\n")

    def order_windows_in_main_screen(self):
        sap_windows = [w for w in gw.getWindowsWithTitle('SAP Easy Access')]
    
        if not sap_windows:
            print("No SAP windows found.")
            return

        # Filter out minimized or "invisible" windows if necessary
        num_windows = len(sap_windows)

        # Standard 1080p resolution (adjust for your laptop)
        screen_width, screen_height = 1280, 752

        # nw 1 11 | nw 2 21 | nw 3 31 | nw 4 22 | nw 5 23 | nw 6 23
        rows = num_windows if num_windows<4 else 2
        cols = 1 if num_windows<4 else -(-num_windows//2)

        
        win_width = screen_width // cols
        win_height = screen_height // rows

        for i, win in enumerate(sap_windows):

            col, row = i % cols, i // cols
            x, y = col * win_width, row * win_height

            # Force window out of minimized state
            if win.isMinimized:
                win.restore()
            
            # Fix for the 'Error code 0' issue
            try:
                win.activate()
            except:
                # Alternative way to 'activate' if the standard way fails
                win.minimize()
                win.restore()
            
            # Position and Resize
            win.moveTo(x, y)
            win.resizeTo(win_width, win_height)
            print(f'Width: {win.width} | Height: {win.height} | X: {win.left} | Y: {win.top}')
            
            # Small delay to let Windows catch up
            time.sleep(.5)
        print("✅🪟  SAP session's windows was correctly distributed in he main window\n")

    def launch_sap_gui(self):
        """
        Launches SAP GUI using the provided path to saplogon.exe.
        Waits a few seconds for it to start.
        """
        try:
            subprocess.Popen(self.sap_path)
            time.sleep(5)  # Adjustable delay to allow SAP GUI to initialize
            print("✅🚀  SAP GUI launched successfully.\n")
        except Exception as e:
            print(f"‼️  Error launching SAP GUI: {e}\n")
            sys.exit(1)

    def is_sap_gui_open(self):
        """
        Checks if SAP GUI is running by attempting to get the COM object.
        
        Returns:
            bool: True if SAP GUI is open, False otherwise.
        """
        try:
            win32com.client.GetObject("SAPGUI")
            return True
        except:
            return False