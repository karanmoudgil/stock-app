## A. Docker Install

**Install Brew**
(1) xcode-select --install
(2) curl -fsSL -o install.sh https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh
(3) /bin/bash install.sh
(4) echo >> /Users/kmoudgil/.zprofile
(5) echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/kmoudgil/.zprofile
(6) eval "$(/opt/homebrew/bin/brew shellenv)"

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
Paste the [copied repository URL](https://github.com/karanmoudgil/stock-app.git) when prompted and press Enter.
Choose a local directory on your computer where you want to save the cloned repository.

**Get API key and create .env**
cp .env.example .env
Get the API Key
Use VS Code to update your API Key in .env

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

## C. How to query the cache & database

**Query Redis cache**
# Open a shell in the Redis container
docker exec -it stock_redis sh

# Inside the container, use redis-cli
redis-cli

# Show keys we’ve stored
KEYS quote:*

# Inspect one ticker
GET quote:AAPL
TTL quote:AAPL

# Exit
exit
exit


**Query SQLite database**
# Open a shell in the sqlite helper container
docker exec -it stock_sqlite sh

# Inspect the DB
sqlite3 /data/quotes.db

-- inside sqlite3:
.headers on
.mode column

-- See table(s)
.tables

-- Peek history
SELECT * FROM search_history ORDER BY id DESC LIMIT 20;

-- Filter by ticker
SELECT * FROM search_history WHERE ticker = 'AAPL' ORDER BY id DESC LIMIT 10;

-- Exit sqlite3
.quit

# exit the container shell
exit
