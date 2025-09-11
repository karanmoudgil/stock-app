## A. Docker Install

**Install Brew**
xcode-select --install
curl -fsSL -o install.sh https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh
/bin/bash install.sh
echo >> /Users/kmoudgil/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/kmoudgil/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

**Check if installed**
Brew help

**Install Docker**
brew install --cask docker

**Check if Installed**
docker --version

**Do the required steps in the app; whale icon**


## B. Get the code repo

**Clone the Repo in VS Code**
Click the "Clone Repository" button.
Paste the [copied repository URL](https://github.com/karanmoudgil/stock-app) when prompted and press Enter.
Choose a local directory on your computer where you want to save the cloned repository.

**Get API key and create .env**
cp .env.example .env
Use VS Code to update your API Key

**Safeguard .env**
touch .gitignore
echo ".env" >> .gitignore


## C. Build, run and watch logs

**Build and Run**
docker compose up -d --build

**Watch Logs**
docker logs -f stock_web

**Web Browser**
POST -> http://localhost:8000/
GET -> http://localhost:8000/?ticker=META
DB -> http://localhost:8000/api/history
DEBUG -> http://localhost:8000/debug/quote?ticker=META

