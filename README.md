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
````
# clone the repository
git clone https://github.com/jyn626/acsense.git

# go in the directory
cd ascence

# create an environment
python -m venv .venv

# activate the environment
.venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# go the directory, and create an .env file
touch .env

# get your Github Personal Access Token (PAT),
# open the .env file and assign your PAT with this variable name.
# note: dont enclose the PAT with qoutations ("")  
GITHUB_TOKEN=...

# double click on the `run.bat` file, or alternatively you can run it in the terminal with
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
