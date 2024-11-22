import apsync as aps
import anchorpoint as ap
import sys
import json
import os
from datetime import datetime

def extract_first_subfolder(project_path, full_path):
    # Normalize paths to ensure consistent separators
    project_path = os.path.normpath(project_path)
    full_path = os.path.normpath(full_path)
    
    # Remove the project path from the full path
    relative_path = os.path.relpath(full_path, project_path)
    
    # Split the relative path and get the first component
    first_subfolder = relative_path.split(os.sep)[0]
    
    return first_subfolder

def main():
    arguments = sys.argv[1] 
    arguments = arguments.replace("\\", "\\\\")
    database = aps.get_api()
    msg = ""
    path = ""
    ctx = ap.get_context()

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

    test_folder = os.path.join(project.path,first_subfolder,"4_Concept_Renders/1_Tests/",os.path.splitext(os.path.basename(path))[0])
    final_folder = os.path.join(project.path,first_subfolder,"4_Concept_Renders/3_Final/",os.path.splitext(os.path.basename(path))[0])

    database.attributes.set_attribute_value(task,"Artist", ctx.email)
    database.attributes.set_attribute_value(task,"Date", today_date)

    database.attributes.set_attribute_value(task,"File", os.path.relpath(path,project.path).replace("\\","/"))
    
    print(f"The file has been published in SKU {first_subfolder}")

if __name__ == "__main__":
    main()



