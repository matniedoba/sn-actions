import platform
import subprocess
import anchorpoint as ap
import apsync as aps
import os
import re


def create_sku_dialog(sku_options):
    # Create a new dialog
    dialog = ap.Dialog()
    dialog.title = "Pick SKU Type"

    # Get the context and list visible folders
    ctx = ap.Context.instance()

    # Add a dropdown with the label "SKU Type"

    dropdown_enabled = False
    if len(sku_options) > 1:
        dropdown_enabled = True

    dialog.add_text("SKU Type").add_dropdown(
        sku_options[0],
        sku_options,
        var="sku_type",
        callback=dropdown_switched,
        enabled=dropdown_enabled,
    )

    dialog.add_checkbox(default=True, text="Create new increment", var="increment")

    dialog.add_info(
        "Copy the latest version as a new incremental<br>save and open it in Cinema 4D"
    )

    dialog.add_button("Open", var="button", callback=button_clicked)

    # Show the dialog
    dialog.show()


def button_clicked(dialog):
    sku = dialog.get_value("sku_type")
    new_increment = dialog.get_value("increment")
    launch_cinema_4d(sku, new_increment)
    dialog.close()


def dropdown_switched(dialog, value):
    if value != "SKU Type":
        dialog.set_enabled("button", True)


def launch_cinema_4d(sku, new_increment):
    # Define the Cinema 4D content folder path, that is based on the folder structure
    cinema_4d_content_folder = "3_Scenes/1_Cinema4D"

    # Logic to launch Cinema 4D
    ctx = ap.Context.instance()
    target_folder = os.path.join(ctx.project_path, sku, cinema_4d_content_folder)

    if not os.path.isdir(target_folder) or not os.listdir(target_folder):
        ap.UI().show_error(
            "No Cinema 4D folder found",
            f"Cannot find or folder is empty: {cinema_4d_content_folder}",
        )
        return

    # Regular expression to match the increment pattern
    increment_pattern = r"_(?:v)?(\d+).c4d$"

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
            if (
                highest_existing_increment is None
                or increment > highest_existing_increment
            ):
                highest_existing_increment = increment
                highest_new_increment = increment + 1

    # Print the highest existing and new increment values
    if highest_existing_increment is not None:
        existing_file = os.path.join(
            target_folder, f"{sku}_v{highest_existing_increment:03d}.c4d"
        )

        if new_increment:
            new_file = os.path.join(
                target_folder, f"{sku}_v{highest_new_increment:03d}.c4d"
            )
            aps.copy_file(existing_file, new_file)
            if platform.system() == "Windows":
                os.startfile(new_file)
            else:  # macOS or Linux
                subprocess.call(["open", new_file])
            ap.UI().show_success(
                "Opening Cinema 4D", f"Opening {sku}_v{highest_new_increment:03d}.c4d"
            )
        else:
            if platform.system() == "Windows":
                os.startfile(existing_file)
            else:  # macOS or Linux
                subprocess.call(["open", existing_file])
            ap.UI().show_success(
                "Opening Cinema 4D",
                f"Opening {sku}_v{highest_existing_increment:03d}.c4d",
            )
    else:
        ap.UI().show_error(
            "No Cinema 4D file found",
            f"Check the folder {cinema_4d_content_folder} 4D and see if there is any Cinema 4D file located",
        )


def main():
    ctx = ap.Context.instance()
    sku_options = [
        f.name
        for f in os.scandir(ctx.project_path)
        if f.is_dir() and not f.name.startswith(".")
    ]

    if len(sku_options) >= 1:
        create_sku_dialog(sku_options)
    else:
        ap.UI().show_info(
            "No SKU available", "First create a new SKU, then launch Cinema 4D"
        )


if __name__ == "__main__":
    main()
