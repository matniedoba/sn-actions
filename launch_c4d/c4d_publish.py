import apsync as aps
import anchorpoint as ap
import sys
import json
import os
from datetime import datetime
import re

def extract_first_subfolder(project_path, full_path):
    # Normalize paths to ensure consistent separators
    project_path = os.path.normpath(project_path)
    full_path = os.path.normpath(full_path)
    
    # Remove the project path from the full path
    relative_path = os.path.relpath(full_path, project_path)
    
    # Split the relative path and get the first component
    first_subfolder = relative_path.split(os.sep)[0]
    
    return first_subfolder
    
def get_master_name(filepath,appendix):
    # Extract the filename from the filepath
    filename, extension = os.path.splitext(os.path.basename(filepath))
    
    match = re.search(r'(.*?)(?:_v?(\d+))(?:_|$)', filename, re.IGNORECASE)
    if match:
        return match.group(1)+appendix+extension
    
    # If no match with underscore, try matching 'v' followed by digits at the end
    match = re.search(r'(.*?v)(\d+)$', filename, re.IGNORECASE)
    if match:
        return match.group(1)+appendix+extension
    
    # If still no match, try matching any digits at the end
    match = re.search(r'(.*?)(\d+)$', filename)
    if match:
        return match.group(1)+appendix+extension
    
    return filename+appendix+extension

def main():
    arguments = sys.argv[1] 
    arguments = arguments.replace("\\", "\\\\")
    database = ap.get_api()
    msg = ""
    path = ""
    ctx = ap.get_context()
    appendix = "_master"

    # Parse the JSON string
    try:
        parsed_arguments = json.loads(arguments)
        #raise Exception("The output could not be read")
        # Access and print the "msg" object
        if "msg" in parsed_arguments:
            msg = parsed_arguments["msg"]
        if "path" in parsed_arguments:
            path = parsed_arguments["path"]
        else:
            raise Exception("The output could not be read")
    except json.JSONDecodeError:
        raise Exception("Failed to decode JSON.")

    project = aps.get_project(path)
    first_subfolder = extract_first_subfolder(project.path, path)
    task_list = database.tasks.get_task_list(project.path, first_subfolder)
    
    # Check if the task_list is empty and create a new one if necessary
    if not task_list:
        task_list = database.tasks.create_task_list(project.path, first_subfolder)

    task = database.tasks.create_task(task_list, msg)
    database.tasks.set_task_icon(task, aps.Icon(icon_path=":/icons/Misc/single Version.svg",color=""))

    today_date = datetime.now()    
    relative_file_path = os.path.relpath(path,project.path).replace("\\","/")

    database.attributes.set_attribute_value(task,"Artist", ctx.email)
    database.attributes.set_attribute_value(task,"Date", today_date)
    database.attributes.set_attribute_value(task,"Source File", relative_file_path)
    
    master_path = os.path.join(os.path.dirname(path),get_master_name(path, appendix))
    aps.copy_file(path, master_path, True)
    database.attributes.set_attribute_value(master_path,"Source File", os.path.basename(path)+"/")
    
    print(f"The file has been published in SKU {first_subfolder}")

if __name__ == "__main__":
    main()



