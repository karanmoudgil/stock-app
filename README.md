## A. Docker Install

**(A.1) Install Brew**
```console
xcode-select --install

curl -fsSL -o install.sh https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh

/bin/bash install.sh

echo >> /Users/kmoudgil/.zprofile

echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/kmoudgil/.zprofile

eval "$(/opt/homebrew/bin/brew shellenv)"
```

**(A.2) Check if installed**
```console
brew help
```

**(A.3) Install Docker**
```console
brew install --cask docker
```

**(A.4) Check if Installed**
```console
docker --version
```

**(A.5) Do the required steps in the app; whale icon**


## B. Get the code repo

**(B.1) Clone the Repo in VS Code**

(1) Click the "Clone Repository" button.

(2) Paste the [copied repository URL](https://github.com/karanmoudgil/stock-app.git) when prompted and press Enter.

(3) Choose a local directory on your computer where you want to save the cloned repository.


**(B.2) Get API key and create .env**

(1) Copy example and create a .env
```console
cp .env.example .env
```
(2) Get the API Key.

(3) Use VS Code to update your API Key in .env.


**(B.3) Safeguard .env**
```console
touch .gitignore

echo ".env" >> .gitignore
```


## C. Build, run and watch logs

**(C.1) Build and Run**
```console
docker compose up -d --build
```

**(C.2) Watch Logs**
```console
docker logs -f stock_web
```

**(C.3) Web Browser**

(1) POST -> http://localhost:8000/

(2) GET -> http://localhost:8000/?ticker=META

(3) DB -> http://localhost:8000/api/history

(4) DEBUG -> http://localhost:8000/debug/quote?ticker=META


## D. How to query the cache & database

### (D.1) Query Redis cache
**(D.1.1) Open a shell in the Redis container**
```console
docker exec -it stock_redis sh
```

**(D.1.2) Inside the container, use redis-cli**
```console
redis-cli
```

**(D.1.3) Inspect one ticker**
```console
GET quote:AAPL

TTL quote:AAPL
```

**(D.1.4) Exit**
```console
exit
exit
```


### (D.2) Query SQLite database
**(D.2.1) Open a shell in the sqlite helper container**
```console
docker exec -it stock_sqlite sh
```

**(D.2.2) Inspect the DB**
```console
sqlite3 /data/quotes.db
```

```console
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
```

**(D.2.3) exit the container shell**
```console
exit
```
