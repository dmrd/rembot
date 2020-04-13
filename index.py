"""Telegram Remnote bot

now secrets add telegram-token TOKEN
now secrets add remnote-user USER_TOKEN
now secrets add remnote-token TOKEN
now secrets add remnote-parent PARENTID
"""
import os
import logging
import telegram
import requests
import json

from flask import Flask, jsonify, Response, request
app = Flask(__name__)


def send_to_remnote(text, parentId=None, addToEditLater=False):
  parentId = os.getenv('REMNOTE_PARENT')
  data = {
    "apiKey": os.getenv('REMNOTE_TOKEN'),
    "userId": os.getenv('REMNOTE_USER'),
    "text": text,
    "parentId": parentId,
    "addToEditLater": addToEditLater
  }
  data = json.dumps(data)
  r = requests.post(url='https://www.remnote.io/api/v0/create', data=data)
  return r
# send_to_remnote('test message')

_STATE = dict(listen=True)
@app.route('/api', methods=['GET', 'POST'])
def api():
    global _listen
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        return jsonify({"status": "error", "reason": "no tg token"})
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    # debug
    # data = {
    #   "telegram": os.getenv('TELEGRAM_TOKEN'),
    #   "parent": os.getenv('REMNOTE_PARENT'),
    #   "apiKey": os.getenv('REMNOTE_TOKEN'),
    #   "userId": os.getenv('REMNOTE_USER'),
    # }
    # print(data)
    # print(_STATE)

    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        text = update.message.text
        chat_id = update.message.chat.id
        if text == '/listen':
          _STATE['listen'] = not _STATE['listen']
          text = 'Listening mode is now %s' % str(_STATE['listen'])
          bot.sendMessage(chat_id=chat_id, text=text)
        elif _STATE['listen'] or text.startswith('/r'):
          if text.startswith('/') and ' ' in text:
            text = text[text.index(' ') + 1:]
          status = send_to_remnote(text=text)
          # Reply with status code & text
          bot.sendMessage(chat_id=chat_id, text='rem %s: `%s`' % (str(status), text))

    return jsonify({"status": "ok"})

@app.route('/')
def home():
    return 'Welcome to Rembot. Send a message @dmrdbot on telegram'


if __name__ == '__main__':
    app.run(debug=True)
