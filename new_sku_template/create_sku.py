import anchorpoint as ap
import apsync as aps
import os
import re

def create_sku_from_template():
    # Define the path to the template directory
    template_dir = os.path.join(os.path.dirname(__file__), "template")
    
    # Get the list of subfolders in the template directory
    subfolders = next(os.walk(template_dir))[1]
    
    if not subfolders:
        ap.UI().show_info("No templates available", "Please add a template in the 'template' folder.")
        return
    
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
    
    for var in variables.keys():
        dialog.add_text(var, width=72).add_input("", var=var)
    
    def on_create(dialog):
        # Update variables with user input
        for var in variables.keys():
            variables[var] = dialog.get_value(var)
        
        # Define the target folder
        target_folder = ap.get_context().path
        
        # Resolve the template folder name with variables
        resolved_folder_name = aps.resolve_variables(template_folder_name, variables)
        target_path = os.path.join(target_folder, resolved_folder_name)
        
        # Copy the template folder with variables replaced
        aps.copy_from_template(first_template_folder, target_path, variables)
        
        dialog.close()
        ap.UI().show_success("SKU created successfully")
    
    dialog.add_button("Create", callback=on_create)
    dialog.show()

# Call the function to execute the action
create_sku_from_template()

