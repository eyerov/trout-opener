import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QSystemTrayIcon
from PyQt5.QtGui import QIcon

import subprocess
import psutil
import webbrowser

class RosLaunchApp(QWidget):
    def __init__(self):
        super().__init__()

        self.start_roscore()

        self.launch_processes = {}  # Dictionary to store process objects
        self.buttons = {}  # Dictionary to store buttons

        # Define launch file information as a list of tuples (package_name, launch_file_name)
        self.launch_files = [
            ('mavros', 'apm.launch fcu_url:=udp://:14555@'),
            ('rosbridge_server', 'rosbridge_websocket.launch'),
            ('joystick_controller', 'joystick_controller.launch'),
            ('usbl_ros', 'usbl_ros.launch'),
            ('ut_data_extractor', 'ut_probe.launch'),
            ('external_temp', 'external_mavros.launch'),
            ('uwrov', 'sonar.launch'),
            ('map_downloader', 'map_downloader.launch'),
            ('oven_media_recoder', 'recorder.launch'),
            ('notification_sender', 'notification_sender.launch'),
            ('heading_depth_sender', 'sender.launch'),
            ('waterlinked_a50_ros_driver', 'launch_dvl.launch'),
        ]

        self.app_launches = [
            ('Joystick_Configurator', 'joystick.sh'),
            ('Main_App', 'ichub.sh'),
        ]

        self.init_ui()
    
    def start_roscore(self):
        # Start roscore if it's not already running
        try:
            self.roscore_process = subprocess.Popen(['roscore'])
            print("roscore started successfully.")
        except Exception as e:
            print(f"Error starting roscore: {e}")

    def stop_roscore(self):
        # Terminate the roscore process
        if hasattr(self, 'roscore_process') and self.roscore_process.poll() is None:
            try:
                pid = self.roscore_process.pid
                process = psutil.Process(pid)
                process.terminate()
                self.roscore_process.wait()
                print("roscore terminated successfully.")
            except Exception as e:
                print(f"Error stopping roscore: {e}")

    def init_ui(self):
        # Create a single button to start/stop all ROS nodes
        self.toggle_all_button = QPushButton('Start All Nodes', self)
        self.toggle_all_button.clicked.connect(self.toggle_all_ros_nodes)

        layout = QVBoxLayout()

        layout.addWidget(self.toggle_all_button)

        for i, (package_name, launch_file_name) in enumerate(self.launch_files):
            h_box = QHBoxLayout()
            name_label = QLabel(package_name)
            action_button = QPushButton(f'Start ROS Launch {i + 1}', self)
            action_button.clicked.connect(lambda _, package=package_name, launch=launch_file_name: self.toggle_ros_launch(package, launch))

            h_box.addWidget(name_label)
            h_box.addWidget(action_button)

            layout.addLayout(h_box)
            self.buttons[f'Start ROS Launch {i + 1}'] = action_button
        
        label = QLabel("Apps:")

        layout.addWidget(label)

        for i, (package_name, launch_file_name) in enumerate(self.app_launches):
            h_box = QHBoxLayout()
            name_label = QLabel(package_name)
            action_button = QPushButton(f'Start App {i + 1}', self)
            action_button.clicked.connect(lambda _, package=package_name, launch=launch_file_name: self.toggle_app_launch(package, launch))

            h_box.addWidget(name_label)
            h_box.addWidget(action_button)
            layout.addLayout(h_box)
            self.buttons[f'Start App {i + 1}'] = action_button

        self.setLayout(layout)
        self.setWindowTitle('EyeROV Trout Opener')

        icon_path = 'icon.png'
        tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        self.setWindowIcon(QIcon(icon_path))
        tray_icon.setToolTip('EyeROV Trout Opener')
        tray_icon.show()

        self.show()

    def toggle_all_ros_nodes(self):
        if self.toggle_all_button.text() == 'Start All Nodes':
            # If the button text is 'Start All Nodes', start all nodes
            for package_name, launch_file_name in self.launch_files:
                self.start_ros_launch(package_name, launch_file_name)
            self.toggle_all_button.setText('Stop All Nodes')
        else:
            # If the button text is 'Stop All Nodes', stop all nodes
            for package_name, launch_file_name in self.launch_files:
                self.stop_ros_launch(package_name, launch_file_name)
            self.toggle_all_button.setText('Start All Nodes')

    def toggle_ros_launch(self, package_name, launch_file_name):
        launch_file_path = f"{package_name} {launch_file_name}"

        if launch_file_path in self.launch_processes and self.launch_processes[launch_file_path].poll() is None:
            # If the process is running, stop it
            self.stop_ros_launch(package_name, launch_file_name)
        else:
            # If the process is not running, start it
            self.start_ros_launch(package_name, launch_file_name)

    def toggle_app_launch(self, package_name, launch_file_name):
        launch_file_path = f"{launch_file_name}"

        if launch_file_path in self.launch_processes and self.launch_processes[launch_file_path].poll() is None:
            # If the process is running, stop it
            self.stop_app_launch(package_name, launch_file_name)
        else:
            # If the process is not running, start it
            self.start_app_launch(package_name, launch_file_name)

    def start_ros_launch(self, package_name, launch_file_name):
        launch_file_path = f"{package_name} {launch_file_name}"

        print(f"Starting : {launch_file_path}")

        if launch_file_path in self.launch_processes and self.launch_processes[launch_file_path].poll() is None:
            print(f"ROS Launch file {launch_file_path} is already running.")
            return

        # Construct the roslaunch command
        roslaunch_cmd = f"roslaunch {launch_file_path}"

        # Use subprocess.Popen to start the roslaunch process and retrieve its PID
        try:
            process = subprocess.Popen(roslaunch_cmd, shell=True)
            self.launch_processes[launch_file_path] = process
            self.update_button_text(package_name, launch_file_name, is_running=True)
        except Exception as e:
            print(f"Error starting ROS Launch file {launch_file_path}: {e}")

    def start_app_launch(self, package_name, launch_file_name):
        launch_file_path = f"{launch_file_name}"

        print(f"Starting : {launch_file_path}")

        if launch_file_path in self.launch_processes and self.launch_processes[launch_file_path].poll() is None:
            print(f"App {launch_file_path} is already running.")
            return

        # Construct the roslaunch command
        roslaunch_cmd = f"./{launch_file_path}"

        # Use subprocess.Popen to start the roslaunch process and retrieve its PID
        try:
            process = subprocess.Popen(roslaunch_cmd, shell=False)
            self.launch_processes[launch_file_path] = process
            self.update_app_button_text(package_name, launch_file_name, is_running=True)
            if package_name == 'Main_App':
                webbrowser.open('http://localhost:5173')
        except Exception as e:
            print(f"Error starting App file {launch_file_path}: {e}")

    def stop_ros_launch(self, package_name, launch_file_name):
        launch_file_path = f"{package_name} {launch_file_name}"

        if launch_file_path in self.launch_processes and self.launch_processes[launch_file_path].poll() is None:
            try:
                # Get the process ID (PID) of the roslaunch process
                pid = self.launch_processes[launch_file_path].pid

                # Terminate the process using psutil
                process = psutil.Process(pid + 1)
                process.terminate()

                # Wait for the process to finish
                self.launch_processes[launch_file_path].wait()

                print(f"ROS Launch file {launch_file_path} terminated successfully.")
            except Exception as e:
                print(f"Error stopping ROS Launch file {launch_file_path}: {e}")

            self.update_button_text(package_name, launch_file_name, is_running=False)

    def stop_app_launch(self, package_name, launch_file_name):
        launch_file_path = f"{launch_file_name}"

        if launch_file_path in self.launch_processes and self.launch_processes[launch_file_path].poll() is None:
            try:
                # Get the process ID (PID) of the roslaunch process
                pid = self.launch_processes[launch_file_path].pid

                # Terminate the process using psutil
                process = psutil.Process(pid + 1)
                process.terminate()

                # Wait for the process to finish
                self.launch_processes[launch_file_path].wait()

                print(f"App {launch_file_path} terminated successfully.")
            except Exception as e:
                print(f"Error stopping App file {launch_file_path}: {e}")

            self.update_app_button_text(package_name, launch_file_name, is_running=False)

    def update_button_text(self, package_name, launch_file_name, is_running):
        index = self.launch_files.index((package_name, launch_file_name))
        button = self.buttons.get(f'Start ROS Launch {index + 1}')

        if button:
            if is_running:
                button.setText(f'Stop ROS Launch {index + 1}')
            else:
                button.setText(f'Start ROS Launch {index + 1}')

    def update_app_button_text(self, package_name, launch_file_name, is_running):
        index = self.app_launches.index((package_name, launch_file_name))
        button = self.buttons.get(f'Start App {index + 1}')

        if button:
            if is_running:
                button.setText(f'Stop App {index + 1}')
            else:
                button.setText(f'Start App {index + 1}')
    def closeEvent(self, event):
        # Override the closeEvent method to stop roscore when the application is closed
        self.stop_roscore()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RosLaunchApp()
    sys.exit(app.exec_())
