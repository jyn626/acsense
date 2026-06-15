> [!NOTE]
> Developed as a learning project. Some features may be incomplete or subject to change.

# acsense
detects your current activity (coding, browsing, youtube.) and keeps your github status in sync automatically.

## Features as of now
-  Detects opened IDE: `Visual Studio Code` and `Zed`.
-  Get exact title of the Youtube video the user is watching, via a browser extension.
-  Prioritizes coding activity to be displayed in the github status.
-  Detecs if there are no IDE opened by checking list of processes, if there are none then display the others respectively by priority.

## Usage
<small>Windows Powershell</small>
````
# 1. Clone the repository and move into the correct directory
git clone https://github.com/jyn626/acsense.git
cd acsense

# 2. Set up and activate the virtual environment
python -m venv .venv
& .\.venv\Scripts\Activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Prompt for your GitHub token and automatically write it to the .env file
$token = Read-Host "Paste your GitHub Personal Access Token (PAT) here (No quotes needed)"
"GITHUB_TOKEN=$token" | Out-File -FilePath .env -Encoding utf8

# 5. Launch the application, double click on the run.bat file or run:
.\run.bat
````
load the browser extension,
go to `chrome://extensions` on your browser
1. Enable `developer mode`
2. Select `load unpacked`
3. And finally, select the `extension` folder. 

## Dependencies
-  psutil
-  requests
-  pywin32
-  python-dotenv
-  Flask
-  flask-cors

## License

This project is licensed under the [MIT licence](LICENSE)
