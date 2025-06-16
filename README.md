# Product Viz case

This repository contains tools and scripts to streamline the workflow for creating and publishing new SKUs (product numbers) using Cinema 4D and Anchorpoint.

## Contents

- **cinema_4d_plugin/Anchorpoint/**
  - Contains the Cinema 4D plugin and the publish script (`publish.pyp`).
  - The plugin adds a menu entry "Anchorpoint/ Publish" in Cinema 4D.
  - When selected, it opens a dialog for the user to enter a comment and then publishes the current Cinema 4D file to Anchorpoint, adding relevant attributes and tasks.
  - The actual publishing logic is handled by `sn_publish_action.py` in the same folder.

- **new_sku_template/**
  - Contains scripts and templates for creating a new SKU (product number) project.
  - `create_sku.py` and `create_sku.yaml` automate the creation of a new project folder with a fixed structure, based on a specified template location.
  - After creating the template, Cinema 4D is automatically launched for the user to begin work.

- **launch_c4d/**
  - Checks for all SKU parts and opens a dialog that will let the user pick which scene should be opened
  - Then it will also allow the user to create a new increment and then start Cinema 4D

## Workflow Overview

1. **Create a New SKU**
   - Run the script in `new_sku_template` to create a new SKU (product number) project.
   - The script will generate a folder structure based on the template location (which must be set in the action settings).
   - Once the template is created, Cinema 4D will launch automatically for the user to start working.

2. **Publish the Work**
   - After finishing the work in Cinema 4D, use the menu entry "Anchorpoint/ Publish".
   - This triggers the plugin, which opens a dialog for a comment and then runs the publish script.
   - The script adds the necessary attributes and tasks in Anchorpoint for the published file.

## Installation for the user

1. **Import the Action in the Anchorpoint workspace settings**

2. **Install the Cinema 4D Plugin**
   - Set the path to the `cinema_4d_plugin` folder in your Cinema 4D plugin settings.

3. **Set the Template Location**
   - Configure the template location for both Windows and Mac in the action settings (see `template_settings.py` in `new_sku_template`).


## Development tips

Create a main project folder, that will contain the template, the code repository and a test project. Create a testproject in Anchorpoint. For templates, take a look at the template_example.zip

---

For more details, refer to the scripts and comments in each folder.
