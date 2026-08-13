# Developer Guide: How to Run the Batch Launcher in VS Code

This guide explains how to open, execute, and configure the Windows batch launcher (`run_app.bat`) within Microsoft Visual Studio Code (VS Code).

---

## Method 1: The VS Code Integrated Terminal (Recommended)

This is the fastest, standard way to execute a batch file inside VS Code.

1. **Open your project folder** in VS Code:
   - Go to: **File -> Open Folder...** and select `Apple_Change_Detection_POC`.
2. **Open the Integrated Terminal**:
   - Use the keyboard shortcut: **`Ctrl + ` `** (Control + Backtick)
   - Or navigate to: **Terminal -> New Terminal** from the top menu.
3. **Verify Terminal Shell**:
   - Ensure your terminal dropdown profile is set to **Command Prompt (cmd.exe)** on Windows.
   - If it is PowerShell or Bash, click the dropdown arrow next to the `+` sign on the terminal header and select **Command Prompt**.
4. **Execute the batch file**:
   - Simply type the following and press **Enter**:
     ```cmd
     run_app.bat
     ```
   - The launcher will activate the virtual environment and start the Streamlit app automatically!

---

## Method 2: Configure as an Automated VS Code Task

You can register the batch file as an automated task in VS Code so you can trigger it at any time with a single command from the Command Palette.

1. In the project root, create a folder named `.vscode/` (if it does not exist).
2. Create a file named `tasks.json` inside the `.vscode/` folder.
3. Paste the following JSON task configuration:
   ```json
   {
     "version": "2.0.0",
     "tasks": [
       {
         "label": "Run Streamlit App (Windows)",
         "type": "shell",
         "command": "cmd.exe",
         "args": ["/c", "run_app.bat"],
         "group": {
           "kind": "test",
           "isDefault": true
         },
         "presentation": {
           "reveal": "always",
           "panel": "shared"
         }
       }
     ]
   }
   ```
4. **How to Launch the App using the Task**:
   - Press **`Ctrl + Shift + P`** (to open the Command Palette).
   - Type **`Run Task`** and press Enter.
   - Select **`Run Streamlit App (Windows)`** from the menu.

---

## Method 3: Visual Play Button (Code Runner Extension)

If you prefer a one-click visual button:

1. Click on the **Extensions** icon on the left sidebar (shortcut: `Ctrl + Shift + X`).
2. Search for and install the extension **`Code Runner`**.
3. Once installed, simply open `run_app.bat` in the editor, and click the **Run Code** play button in the top-right corner, or right-click the file in the Explorer pane and select **Run in Terminal**.
