#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022 Emil Suleymanov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import argparse
import json
import os
import re
import shutil
import time
from random import random

import requests
from telethon import TelegramClient
from telethon import events
from telethon.tl.types import Channel, User

parser = argparse.ArgumentParser(description='Start the frog killer bot')
parser.add_argument('--api_id', metavar='api_id', required=True,
                    help='Telegram API ID')
parser.add_argument('--api_hash', metavar='api_hash', required=True,
                    help='Telegram API hash')
args = parser.parse_args()

api_id = int(args.api_id)
api_hash = args.api_hash

COOLDOWN_S = 60
MAX_PER_COOLDOWN_PERIOD = 300

cooldown_start = 0
count_since_cooldown_start = 0

user_client = TelegramClient('frog_killer_session', api_id, api_hash)

foreign_shit_message_ids = dict()

yasru_filter = re.compile('#я[сc][рp][уy]', re.IGNORECASE)

nos_list = ["no", "nei", "nay", "nah", "nö", "nein", "нет", "nope", "nop", "nada", "nah", "yox", "heyir", "hayir"]
yous_list = ["you", "u", "ye", "du", "ты", "sən", "sen"]
breaks_list = [r",", r".", r"\-", r" ", r"\n"]
nos_regex = '|'.join(nos_list)
yous_regex = '|'.join(yous_list)
breaks_regex = re.compile("[" + ''.join(breaks_list) + "]")
clean_str_regex = re.compile("^(" + nos_regex + ")|(" + yous_regex + ")$")

cat_url = 'https://some-random-api.ml/img/cat'


def is_nou(message_srt):
    print("original: " + message_srt)
    # normalize string
    # lower case all
    message_srt = message_srt.lower()
    # remove the break chars
    message_srt = breaks_regex.sub("", message_srt)
    # collapse duplicates
    tmp_message_srt = ""
    last_c = ""
    for c in message_srt:
        if c != last_c:
            tmp_message_srt += c
            last_c = c
    message_srt = tmp_message_srt
    print("normal: " + message_srt)
    # test with regex
    return clean_str_regex.match(message_srt) is not None


@user_client.on(events.MessageDeleted())
async def handler(event):
    # Log all deleted message IDs
    for msg_id in event.deleted_ids:
        if msg_id in foreign_shit_message_ids:
            print('foreign_shit_message_ids:', msg_id, 'was deleted in', event.chat_id)
            to_delete_msg = await user_client.get_messages(event.chat_id,
                                                           ids=foreign_shit_message_ids[msg_id])
            if to_delete_msg.message.lower() == "#йееей":
                print('foreign_shit_message_ids:', msg_id, 'was deleted in', event.chat_id, "; confirmed text; del")
                await user_client.delete_messages(event.chat_id, [foreign_shit_message_ids.pop(msg_id)])


def cooldown():
    global cooldown_start
    global count_since_cooldown_start

    print(F"{cooldown_start}, {count_since_cooldown_start}")

    result = False

    if count_since_cooldown_start < MAX_PER_COOLDOWN_PERIOD:
        count_since_cooldown_start += 1
        result = True

    if time.time() - cooldown_start > COOLDOWN_S:
        cooldown_start = time.time()
        count_since_cooldown_start = 0

    return result


@user_client.on(events.NewMessage())
async def handler(event):
    sender = await event.get_sender()

    if yasru_filter.match(event.message.message.lower()) and isinstance(sender, User) and not sender.is_self:
        print("foreign shit event detected")
        # reply_msg = await event.reply('#йееей')
        # foreign_shit_message_ids[event.message.id] = reply_msg.id

    if event.message.file is not None and event.message.file.mime_type == 'video/webm' and \
            ((isinstance(sender,
                         Channel) and sender.admin_rights.post_messages and sender.admin_rights.delete_messages)
             or (isinstance(sender, User) and sender.is_self)):
        print("webm self event detected")
        tmp_filename = 'tmp' + str(random()) + '.webm'
        await user_client.download_file(event.message, file=tmp_filename)
        await user_client.delete_messages(entity=event.chat_id, message_ids=[event.message.id])
        os.system("ffmpeg -i " + tmp_filename + " -movflags faststart -pix_fmt yuv420p -vf"
                                                " \"scale=trunc(iw/2)*2:trunc(ih/2)*2\" " + tmp_filename + ".mp4")
        await user_client.send_file(entity=event.chat_id, file=tmp_filename + ".mp4")
        os.remove(tmp_filename)
        os.remove(tmp_filename + ".mp4")

    if is_nou(event.message.message):
        if cooldown():
            print("No u")
            await event.reply('No u')

    if event.message.message == 'getPussy()':
        if cooldown():
            cat_link = json.loads(requests.get(cat_url).text)["link"]
            filename = cat_link.split("/")[-1] + ".jpeg"
            r = requests.get(cat_link, stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                with open(filename, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                await event.reply(file=filename)
                os.remove(filename)


async def user_main():
    await user_client.send_message('me', 'Hello, myself!')


with user_client:
    user_client.loop.run_until_complete(user_main())
    user_client.run_until_disconnected()
