import anchorpoint as ap
import apsync as aps
import os

def create_sku_dialog(sku_options):
    # Create a new dialog
    dialog = ap.Dialog()
    dialog.title = "Pick SKU Type"

    # Get the context and list visible folders
    ctx = ap.Context.instance()

    # Add a dropdown with the label "SKU Type"
    dialog.add_text("SKU Type").add_dropdown("SKU Type", sku_options, var="sku_type", callback=dropdown_switched).add_button("Open", var="button", callback=button_clicked, enabled=False)

    # Show the dialog
    dialog.show()

def button_clicked(dialog):
    sku = dialog.get_value("sku_type")
    launch_cinema_4d(sku)
    dialog.close()
   
def dropdown_switched(dialog,value):
    if value != "SKU Type":
        dialog.set_enabled("button",True)

def launch_cinema_4d(sku):
    # Logic to launch Cinema 4D
    ctx = ap.Context.instance()
    target_folder = os.path.join(ctx.project_path,sku,"3_Scenes/1_Cinema4D")
    import re

    # Regular expression to match the increment pattern
    increment_pattern = r'_(?:v)?(\d+).c4d$'

    # Initialize highest existing and new increment values
    highest_existing_increment = None
    highest_new_increment = None

    # List all files in the target folder
    files = os.listdir(target_folder)
    for file in files:
        # Check if the file matches the SKU and has an increment
        if file.startswith(sku) and re.search(increment_pattern, file):
            # Extract the increment number
            match = re.search(increment_pattern, file)
            increment = int(match.group(1))
            # Update highest existing and new increment values if necessary
            if highest_existing_increment is None or increment > highest_existing_increment:
                highest_existing_increment = increment
                highest_new_increment = increment + 1

    # Print the highest existing and new increment values
    if highest_existing_increment is not None:
        existing_file = os.path.join(target_folder,f"{sku}_v{highest_existing_increment:03d}.c4d")
        new_file = os.path.join(target_folder,f"{sku}_v{highest_new_increment:03d}.c4d")
        aps.copy_file(existing_file,new_file)
        os.startfile(new_file)
        ap.UI().show_success("Opening Cinema 4D",f"Opening {sku}_v{highest_new_increment:03d}.c4d")        
    else:
        ap.UI().show_error("No Cinema 4D file found","Check the folder 3_Scenes/1_Cinema 4D and see if there is any Cinema 4D file located")


def main():    
    ctx = ap.Context.instance()
    sku_options = [f.name for f in os.scandir(ctx.project_path) if f.is_dir() and not f.name.startswith('.')]

    if len(sku_options) > 1:
        create_sku_dialog(sku_options)
    
    elif len(sku_options) == 1:
        launch_cinema_4d(sku_options[0])
    else:
        ap.UI().show_info("No SKU available","First create a new SKU, then launch Cinema 4D")


if __name__ == "__main__":
    main()