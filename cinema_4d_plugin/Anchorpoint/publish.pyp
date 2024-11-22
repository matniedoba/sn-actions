import c4d
from c4d import gui, plugins
import subprocess
import os
import json
import re
import platform
import threading

PLUGIN_ID = 1064547  # Replace with a unique ID


class OpenLatestVersionDialog(gui.GeDialog):
    def CreateLayout(self):
        self.SetTitle("Publish Current Version")

        # Add infotext above the text field
        self.AddStaticText(
            1004, 460, 0, name="Publishing will create a new version in Anchorpoint")

        self.AddMultiLineEditText(1003, c4d.BFH_SCALEFIT, 256, 40)
        self.AddButton(1001, c4d.BFH_SCALEFIT, 256, 0, name="Publish")

        return True

    def OpenDialog(self, dlgtype):
        # Open the dialog in the center of the application
        self.Open(dlgtype, -1, -1)

    def Command(self, id, msg):
        if id == 1001:  # Open button clicked
            # Retrieve the user input from the dialog
            user_message = self.GetString(1003)  # Assuming 1003 is the ID for the input field

            # Check if the user_message is empty
            if not user_message.strip():
                gui.MessageDialog("Please enter a comment")
                return True

            # Start the run_executable function in a new thread with the user_message
            threading.Thread(target=self.run_executable, args=(user_message,)).start()
            self.Close()
        return True

    def run_executable(self, user_message):
        def execute_command():
            try:

                c4d_version = c4d.GetC4DVersion() // 1000                

                # Show busy indicator depending on c4d version
                if c4d_version <= 2024:
                    c4d.StatusSetText("Talking to Anchorpoint")
                    c4d.StatusSetSpin()
                else:
                    gui.StatusSetText("Talking to Anchorpoint")
                    gui.StatusSetSpin() 

                # Path to the executable
                executable_path = get_executable_path()
                
                doc = c4d.documents.GetActiveDocument()
                    
                # Get the path of the currently open document
                document_path = doc.GetDocumentPath()
                document_name = doc.GetDocumentName()
                
                # JSON object, you can extend this
                json_object = {
                    "msg": user_message,
                    "path": os.path.join(document_path, document_name)
                }
                
                # Convert the JSON object to a string
                json_string = json.dumps(json_object)
                    
                # Correctly format the command and its arguments
                command = [
                    executable_path,
                    '--cwd', document_path,
                    'python',
                    '-s',
                    '.ap/c4d_publish.py',
                    '--args',
                    json_string,
                ]

                # Setup to hide the CLI window
                startupinfo = None
                if platform.system() == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE

                # Run the command and capture the output
                result = subprocess.run(command, capture_output=True, text=True, check=True, startupinfo=startupinfo)
                # Check for "script not found" message
                if "script not found" in result.stderr.lower():
                    gui.MessageDialog("This file is not part of an Anchorpoint project.")

                elif result.stderr:  # Print the standard error if there is any
                    print(result.stderr)
                    gui.MessageDialog("An issue has occurred")
                    return
                
                else:
                    # Show success message if no errors
                    gui.MessageDialog(result.stdout)
            
            except subprocess.CalledProcessError as e:
                print(f"An error occurred: {e}")
            
            finally:
                # Hide busy indicator
                if c4d_version <= 2024:
                    c4d.StatusClear()
                else:
                    gui.StatusClear()

        # Run the command in a separate thread
        threading.Thread(target=execute_command).start()


class OpenLatestVersionCommand(plugins.CommandData):
    def Execute(self, doc):
        
        doc = c4d.documents.GetActiveDocument()
        if doc is None or not doc.GetDocumentPath():
            gui.MessageDialog("You have to save your file first")
            return False
        
        dialog = OpenLatestVersionDialog()

        dialog.OpenDialog(c4d.DLG_TYPE_MODAL)
        return True

    def GetResourceString(self):
        return {
            "en": {
                "name": "Publish",
                "description": "Sets your current file as latest version"
            },
            "de": {
                "name": "Veröffentlichen",
                "description": "Kennzeichnet diese Datei als letzte Version"
            }
        }


def EnhanceMainMenu():
    mainMenu = gui.GetMenuResource("M_EDITOR")  # Get main menu resource

    # Create the Anchorpoint menu
    anchorpoint_menu = c4d.BaseContainer()
    anchorpoint_menu.InsData(c4d.MENURESOURCE_SUBTITLE, "Anchorpoint")
    anchorpoint_menu.InsData(c4d.MENURESOURCE_COMMAND,
                             "PLUGIN_CMD_" + str(PLUGIN_ID))

    # Add the Anchorpoint menu to the main menu
    if mainMenu:
        mainMenu.InsData(c4d.MENURESOURCE_STRING, anchorpoint_menu)


def PluginMessage(id, data):
    if id == c4d.C4DPL_BUILDMENU:
        EnhanceMainMenu()


def get_executable_path():
    if platform.system() == "Windows":
        base_path = os.path.join(os.getenv('LOCALAPPDATA'), "Anchorpoint")
        pattern = r"app-(\d+\.\d+\.\d+)"
        cli_executable_name = "ap.exe"

        # Get directories matching the pattern
        versioned_directories = [
            d for d in os.listdir(base_path)
            if re.match(pattern, d)
        ]

        # Sort directories by version
        versioned_directories.sort(key=lambda d: tuple(map(int, re.match(pattern, d).group(1).split('.'))), reverse=True)

        if versioned_directories:
            latest_version_path = os.path.join(base_path, versioned_directories[0])
            cli_path = os.path.join(latest_version_path, cli_executable_name)

            if os.path.exists(cli_path):
                return cli_path
            else:
                raise FileNotFoundError("CLI Not Installed!")

    elif platform.system() == "Darwin":  # macOS
        cli_path = "/Applications/Anchorpoint.app/Contents/Frameworks/ap"

        if os.path.exists(cli_path):
            return cli_path
        else:
            raise FileNotFoundError("CLI Not Installed!")

    else:
        raise OSError("Unsupported OS")


if __name__ == "__main__":
    # Load the icon from the file
    icon = c4d.bitmaps.BaseBitmap()
    icon_path = os.path.join(os.path.dirname(__file__), "ap.png")
    if icon.InitWith(icon_path)[0] != c4d.IMAGERESULT_OK:
        icon = None  # Fallback if the icon fails to load

    # Register the command plugin with the icon
    plugins.RegisterCommandPlugin(
        id=PLUGIN_ID,
        str="Publish",
        info=c4d.PLUGINFLAG_HIDE,  # Hide from Extensions menu
        icon=icon,
        help="Sets this file as a latest version and allows to add a comment",
        dat=OpenLatestVersionCommand()
    )
