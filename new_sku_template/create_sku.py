import anchorpoint as ap
import apsync as aps
import os
import re
import platform


def get_workspace_template_dir():    
    ctx = ap.get_context()    
    settings = aps.SharedSettings(ctx.workspace_id, "SharkNinjaSettings")
    template_dir_win = settings.get("template_dir_win")
    template_dir_mac = settings.get("template_dir_mac")

    if platform.system() == "Darwin":
        return template_dir_mac
    else :
        return template_dir_win

def create_sku_from_template():
    
    template_dir = get_workspace_template_dir()

    # Get the list of subfolders in the template directory
    try:
        if template_dir == "":
            template_dir = os.path.join(os.path.dirname(__file__), "template")        
    
        subfolders = next(os.walk(template_dir))[1]
    except Exception:
        ap.UI().show_info("No templates available", "Please add a path in the action settings")
        return  # Exit the function if an error occurs
        
    # Assume the first subfolder is the template folder
    template_folder_name = subfolders[0]
    first_template_folder = os.path.join(template_dir, template_folder_name)
    
    # Find variables in the template folder name and its contents
    variables = {}
    entry_vars = re.findall(r"\[[^\[\]]*\]", template_folder_name)
    for var in entry_vars:
        variables[var.replace("[", "").replace("]", "")] = None
    
    for root, dirs, files in os.walk(first_template_folder):
        for name in dirs + files:
            entry_vars = re.findall(r"\[[^\[\]]*\]", name)
            for var in entry_vars:
                variables[var.replace("[", "").replace("]", "")] = None
    
    # Create a dialog to get user input for each variable
    dialog = ap.Dialog()
    dialog.title = "Create SKU"
    if ap.get_context().icon:
        dialog.icon = ap.get_context().icon
    
    for var in variables.keys():
        dialog.add_text(var, width=72).add_input("", var=var,placeholder="AB-234-BL")
    
    # Add inputs for "ID Spec" and "UI Spec"
    dialog.add_text("Wrike Task", width=72).add_input("", var="wrike", placeholder="Enter Wrike URL")
    
    def on_create_from_template(dialog):
        dialog.close()
        ap.get_context().run_async(copy_from_template,dialog)
    
    def copy_from_template(dialog):
        progress = ap.Progress("Creating from Template")
        # Update variables with user input
        for var in variables.keys():
            variables[var] = dialog.get_value(var)
        
        # Get the values for "ID Spec" and "UI Spec"
        wrike_url = dialog.get_value("wrike")
        
        # Define the target folder
        target_folder = ap.get_context().project_path
        
        # Resolve the template folder name with variables
        resolved_folder_name = aps.resolve_variables(template_folder_name, variables)
        target_path = os.path.join(target_folder, resolved_folder_name)
        
        # Copy the template folder with variables replaced
        aps.copy_from_template(first_template_folder, target_path, variables)

        database = ap.get_api()

        id_spec_attribute = database.attributes.get_attribute("Wrike")
        if not id_spec_attribute:
            id_spec_attribute = database.attributes.create_attribute(
                "Wrike", aps.AttributeType.hyperlink
            )

        file_attribute = database.attributes.get_attribute("Source File")
        if not file_attribute:
            file_attribute = database.attributes.create_attribute(
                "Source File", aps.AttributeType.hyperlink
            )

        database.attributes.set_attribute_value(target_path,id_spec_attribute, wrike_url)
        
        progress.finish()
        ap.UI().show_success("SKU created successfully")
        ap.UI().reload()
    
    dialog.add_button("Create", callback=on_create_from_template)
    dialog.show()

# Call the function to execute the action
create_sku_from_template()

