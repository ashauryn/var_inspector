# var_inspector
Tool for scraping package names and json key locations from a .var file. Self-executable, written in Python v3.10.6.

VAR Inspector is a useful tool for content creators working with Virt-A-Mate (VaM 1.x).  After creating your in-game package, or .var, load your var in the VAR inspector to determine the name and location of any dependencies included in your scene, presets, or other package content. 

This can help to determine the location of any rogue or unwanted dependencies currently in your scene.

This tool can also be used to determine whether the meta.json information for a particular package is accurate, or to provide the user with a list of primary dependencies that are required for the package to load correctly in-game. 

USE INSTRUCTIONS:

1. Click "Add File" to select your .var (you can select multiple files)
2. Click "submit" to run the inspector
3. Results (if any) will display in the log window and the results table
4. Type in the search bar to locate a specific package
5. Select a single or multiple table cells and right click to copy the list
6. Left-click on a row will display details about the location, such as a morph name or texture file, in the location details box at the bottom
7. Reset to add new files or scan another .var
