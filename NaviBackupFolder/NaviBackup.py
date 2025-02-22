import os
import sys
import subprocess
import requests
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QProgressBar, QTextEdit, QMainWindow, QCheckBox, QHBoxLayout, QToolTip, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt5.QtGui import QIcon, QCursor
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def set_dark_theme(self):
    """Set dark theme for the application."""
    dark_stylesheet = """
    QWidget {
        background-color: #000000;
        color: #ffffff;
    }
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #2a2c31;
        color: #ffffff;
        border: none;
        padding: 5px;
        border-radius: 10px;
    }
    QPushButton {
        background-color: #000000; 
        color: white; 
        font-size: 16px; 
        padding: 10px; 
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #f50000;
    }
    QPushButton:pressed {
        background-color: #FFFFFF;
    }
    QListWidget {
        background-color: #3c3f41;
        color: #d3d3d3;
        border: 1px solid #444444;
    }
    QGroupBox {
        border: 1px solid #444444;
        background-color: #2b2b2b;
        color: #d3d3d3;
        margin: 5px;
        padding: 10px;
    }
    QFormLayout {
        background-color: #2b2b2b;
        color: #d3d3d3;
    }
    """
    self.setStyleSheet(dark_stylesheet)

def set_light_theme(self):
    """Set light theme for the application."""
    light_stylesheet = """
    QWidget {
        background-color: #ffffff;
        color: #000000;
    }
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #ffffff;
        color: #000000;
        border: none;
        padding: 5px;
        border-radius: 10px;
    }
    QPushButton {
        background-color: #000000; 
        color: white; 
        font-size: 16px; 
        padding: 10px; 
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #f50000;
    }
    QPushButton:pressed {
        background-color: #FFFFFF;
    }
    QListWidget {
        background-color: #3c3f41;
        color: #d3d3d3;
        border: 1px solid #444444;
    }
    QGroupBox {
        border: 1px solid #444444;
        background-color: #2b2b2b;
        color: #d3d3d3;
        margin: 5px;
        padding: 10px;
    }
    QFormLayout {
        background-color: #2b2b2b;
        color: #d3d3d3;
    }
    """
    self.setStyleSheet(light_stylesheet)

class BackgroundWidget(QWidget):
    """A small floating widget for background mode."""
    def __init__(self, ai, parent=None):
        super().__init__(parent)
        self.ai = ai
        self.parent = parent  # Reference to the AutomationApp parent

        self.setWindowTitle("Background Mode")
        self.setFixedSize(300, 50)  # Adjust width to fit input and button in one line
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)  # Make background transparent
        self.setStyleSheet("background: transparent;")  # Ensure full transparency
        
        self.move(QApplication.desktop().availableGeometry().width() - self.width() - 10, 703)  # Position to the side

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Enter command...")
        self.input_field.setStyleSheet("font-size: 14px; padding: 5px; border-radius: 5px; background: #3b3838; color: white;")
        self.input_field.setFixedHeight(30)
        self.input_field.returnPressed.connect(self.execute_command)  # Enable Enter key execution

        self.execute_button = QPushButton("▶", self)  # Mini run button
        self.execute_button.setFixedSize(40, 30)  # Smaller button size
        self.execute_button.setStyleSheet("background: #3b3838; color: white; border-radius: 5px; border: 1px solid #ccc;")
        self.execute_button.clicked.connect(self.execute_command)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to avoid unnecessary padding
        layout.setSpacing(5)
        layout.addWidget(self.input_field)
        layout.addWidget(self.execute_button)

        self.setLayout(layout)

        # Enable dragging functionality
        self.old_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def execute_command(self):
        user_command = self.input_field.text().strip()
        if user_command.lower() == "exit":
            self.close()  # Close the background widget
            automation_window.show()  # Show the main automation window again
            cli_window.show()  # Ensure CLI window is shown if in background mode
        elif user_command:
            result = self.ai.execute_command(user_command)
            self.input_field.setText("")  # Clear input field
            QToolTip.showText(self.input_field.mapToGlobal(QPoint(0, -30)), f"Output: {result}", self)

class WindowsAutomationAI:
    def __init__(self):
        self.config_file = "config.json"
        self.API_KEY = None
        self.API_URL = "https://openrouter.ai/api/v1/chat/completions"
        self.MODEL = "meta-llama/llama-3-8b-instruct:free"

        # Check if the config file exists and load the API key
        self.load_api_key()

    def load_api_key(self):
        """Load the API key from a JSON file, or prompt the user to enter it if the file is missing."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as file:
                    data = json.load(file)
                    self.API_KEY = data.get("API_KEY", None)
                    print("Loaded API Key:", self.API_KEY)
            except Exception as e:
                print(f"Error loading API key: {e}")
        if not self.API_KEY:
            # Prompt the user for the API key if not found or invalid
            self.prompt_for_api_key()

    def prompt_for_api_key(self):
        """Prompt the user for the API key if it's not available in the config file."""
        api_key, ok = QInputDialog.getText(None, "Enter API Key", "Please enter your API key:")
        if ok and api_key:
            self.API_KEY = api_key
            print("Loaded API Key:1", api_key)
            self.save_api_key()
        else:
            QMessageBox.critical(None, "Error", "API key is required to proceed.")

    def save_api_key(self):
        """Save the API key to a JSON file."""
        try:
            with open(self.config_file, "w") as file:
                json.dump({"API_KEY": self.API_KEY}, file)
        except Exception as e:
            print(f"Error saving API key: {e}")

    def get_windows_command(self, user_command):
        prompt = f"""
        You are a Windows automation AI. Your task is to convert user input and use a windows command to execute command.
        The user will give you a command in natural language, and you must return only the corresponding Windows command.

        Example 1:
        User: open taskmanager
        Windows Command: taskmgr

        Example 2:
        User: Increase volume by 30%
        Windows Command: nircmd.exe changesysvolume 8192

        Example 3:
        User: Switch to the next tab in Chrome
        Windows Command: nircmd.exe sendkeypress ctrl+tab

        Feel free not to only stick to the examples.
        When generating Windows commands, we only want the Windows command—do not provide explanations or additional information.

        Now, convert the following user command into a Windows command:
        User: {user_command}
        Windows Command:
        """

        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(self.API_URL, headers=headers, json=payload)

        try:
            response_json = response.json()
            if "choices" in response_json and response_json["choices"]:
                windows_command = response_json["choices"][0]["message"]["content"].strip()

                # Validate the returned command
                windows_command = windows_command.lower().strip()

                # Reject responses that start with invalid terms
                if windows_command.startswith("the") or not windows_command or any(word in windows_command for word in ["based", "invalid", "error"]):
                    return None  # Invalid command

                windows_command = windows_command.replace("`", "").strip()
                return windows_command.split("\n")[0].strip()
            else:
                print("Unexpected response format:", response_json)  # Debugging output
                return None
        except Exception as e:
            print(f"Error parsing API response: {e}")
            print("Raw response:", response.text)  # Debugging output

            if not self.API_KEY:
                print("API Key is missing or invalid.")
                print("API URL:", self.API_URL)
            return None

    def execute_command(self, user_command):
        windows_command = self.get_windows_command(user_command)

        if windows_command:
            try:
                # Run the command and capture output
                result = subprocess.run(windows_command, shell=True, text=True, capture_output=True)

                # Get the command's actual output
                output = result.stdout.strip() if result.stdout else result.stderr.strip()

                return output if output else "No output from command."
            except Exception as e:
                return f"Error executing command: {e}"
        else:
            return "Failed to generate a valid command."

class CommandWorker(QThread):
    result_signal = pyqtSignal(str)

    def __init__(self, ai, user_command):
        super().__init__()
        self.ai = ai
        self.user_command = user_command

    def run(self):
        feedback = self.ai.execute_command(self.user_command)
        self.result_signal.emit(feedback)


class AutomationApp(QWidget):
    def __init__(self, cli_window):
        super().__init__()

        self.ai = WindowsAutomationAI()
        self.cli_window = cli_window  # Pass CLI window to AutomationApp

        set_light_theme(self)

        self.setWindowTitle("NaviCoreX")
        self.setFixedSize(400, 250)  # Fixed window size for the main GUI

        icon_path = self.find_icon('NavicoreX/NavicoreX.png')  # Try to find the icon

        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        else:
            self.setWindowIcon(QIcon('NavicoreX/NavicoreX.png'))

        # Accuracy Score Initialization
        self.accuracy = 75  # Starting accuracy

        # Create the no internet label with accuracy display
        self.label = QLabel(self)
        self.label.setText(f"⚠️ If output isn't what you want, retry.\nAccuracy {self.accuracy}%")
        self.label.setStyleSheet("font-size: 16px; padding: 5px;")
        self.label.setAlignment(Qt.AlignCenter)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Enter a command to automate...")
        self.input_field.setStyleSheet("font-size: 16px; padding: 5px;")

        self.execute_button = QPushButton("Execute", self)
        self.execute_button.clicked.connect(self.execute_command)
        self.execute_button.setStyleSheet(set_light_theme(self))

        self.result_label = QLabel("", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 14px; padding: 10px;")

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(""" 
            QProgressBar {
                background-color: #000000;
                border: 1px solid #ffffff;
                border-radius: 10px;
                text-align: center;
                height: 5px;
            }

            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                stop: 0 #ffffff, stop: 1 #ffffff);
                padding: 20px;
                border-radius: 0px;
                width: 5px;
            }
        """)

        self.run_in_background_checkbox = QCheckBox("Run in Background", self)
        self.run_in_background_checkbox.stateChanged.connect(self.toggle_background_mode)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.execute_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.result_label)
        layout.addWidget(self.run_in_background_checkbox)

        self.setLayout(layout)

    def update_accuracy(self, success):
        """Update the accuracy score based on success or failure."""
        if success:
            if self.accuracy < 100:
                self.accuracy += 1  # Increase accuracy
        else:
            if self.accuracy > 0:
                self.accuracy -= 1  # Decrease accuracy
        # Update the label with the new accuracy score
        self.label.setText(f"⚠️ If output isn't what you want, retry.\nAccuracy {self.accuracy}%")

    def find_icon(self, icon_name):
        """Attempts to find the icon in and out of the script's directory."""
        script_dir = os.path.dirname(os.path.realpath(__file__))

        possible_paths = [
            os.path.join(script_dir, icon_name),
            os.path.join(script_dir, 'NavicoreX', icon_name),
            os.path.abspath(os.path.join(script_dir, os.pardir, icon_name)),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def execute_command(self):
        user_command = self.input_field.text()
        if user_command:
            self.progress_bar.setVisible(True)
            self.result_label.setText("Processing your command...")

            # Start the background thread to execute the command
            self.worker = CommandWorker(self.ai, user_command)
            self.worker.result_signal.connect(self.on_result_received)
            self.worker.start()

        else:
            self.result_label.setText("Please enter a command.")

    def on_result_received(self, result):
        self.progress_bar.setVisible(False)
        self.result_label.setText(result)

        # Determine if the result indicates success or failure
        success = False

        if result and "Error" not in result and "invalid" not in result.lower():
            success = True

        # Update the accuracy based on the result of command execution
        self.update_accuracy(success)

        # Log the result in the CLI window
        self.cli_window.log_output(result)

    def toggle_background_mode(self):
        if self.run_in_background_checkbox.isChecked():
            self.cli_window.hide()
            self.hide()
            self.background_widget = BackgroundWidget(self.ai)
            self.background_widget.show()
        else:
            if self.background_widget:
                self.background_widget.close()
            self.show()
            self.cli_window.show()

    def closeEvent(self, event):
        """Override closeEvent to also close the CLI window."""
        self.cli_window.close()
        event.accept()

class CLIWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("INTERFACE")
        self.setFixedSize(600, 400)  # Fixed size for the CLI window
        self.setWindowOpacity(0.9)

        icon_path = self.find_icon('NavicoreX/NavicoreX.png')  # Try to find the icon

        # Set the icon if it's found, otherwise use a fallback
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        else:
            self.setWindowIcon(QIcon('NavicoreX/NavicoreX.png'))

        # Set the dark theme
        set_dark_theme(self)

        # Create a QTextEdit to display the CLI output
        self.cli_output = QTextEdit(self)
        self.cli_output.setReadOnly(True)
        self.cli_output.setStyleSheet("font-size: 14px; padding: 5px;")

        # Create the "Clear" button
        self.clear_button = QPushButton("Clear", self)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #000000; 
                color: white; 
                font-size: 16px; 
                padding: 10px; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #f50000;
            }
            QPushButton:pressed {
                background-color: #FFFFFF;
            }
        """)
        self.clear_button.clicked.connect(self.clear_cli_output)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.cli_output)
        layout.addWidget(self.clear_button)  # Add the button to the layout

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def find_icon(self, icon_name):
        """Attempts to find the icon in and out of the script's directory."""
        script_dir = os.path.dirname(os.path.realpath(__file__))

        possible_paths = [
            os.path.join(script_dir, icon_name),
            os.path.join(script_dir, 'NavicoreX', icon_name),
            os.path.abspath(os.path.join(script_dir, os.pardir, icon_name)),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def log_output(self, output):
        """Log the output to the CLI window."""
        self.cli_output.append(output)

    def clear_cli_output(self):
        """Clear the CLI output."""
        self.cli_output.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create the CLI window and pass it to the main Automation window
    cli_window = CLIWindow()

    # Create and show the main automation window
    automation_window = AutomationApp(cli_window)

    # Create and show the CLI output window
    cli_window.show()

    automation_window.show()

    sys.exit(app.exec_())
