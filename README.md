## YouTube-File

In the file.txt file, you need to write the id of telegram users to whom it is destroyed to use the bot.

### .env.example setup
```
TOKEN = Enter the TOKEN of the telegram bot

ID_TELEGRAM = Enter the ID of users who are given access to use the bot (example: 6467737, 3634643747, 23634777)
```

### Start server bot

```
python3 install -r requirements.txt
```
```
python3 main.py
```

### Docker build

```
docker build . -t youtube-file
```
```
docker run -d youtube-file
```