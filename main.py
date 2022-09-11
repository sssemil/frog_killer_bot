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
import random
import re
import shutil
import time

import requests
from googletrans import Translator
from telethon import TelegramClient
from telethon import events
from telethon.tl.types import Channel, User

parser = argparse.ArgumentParser(description="Start the frog killer bot")
parser.add_argument("--api_id", metavar="api_id", required=True, help="Telegram API ID")
parser.add_argument(
    "--api_hash", metavar="api_hash", required=True, help="Telegram API hash"
)
parser.add_argument(
    "--cooldown_count", metavar="cooldown_count", required=True, help="How many messages per period"
)
parser.add_argument(
    "--cooldown_period", metavar="cooldown_period", required=True,
    help="Length of a cooldown period (both duration and measurements time frame) in seconds"
)
parser.add_argument(
    "--per_user_cooldown_count", metavar="per_user_cooldown_count", required=True,
    help="How many messages per period per user"
)
parser.add_argument(
    "--per_user_cooldown_period", metavar="per_user_cooldown_period", required=True,
    help="Length of a cooldown period (both duration and measurements time frame) in seconds (per user case)"
)
args = parser.parse_args()

api_id = int(args.api_id)
api_hash = args.api_hash

COOLDOWN_S = int(args.cooldown_period)
MAX_PER_COOLDOWN_PERIOD = int(args.cooldown_count)

PER_USER_COOLDOWN_S = int(args.per_user_cooldown_period)
PER_USER_MAX_PER_COOLDOWN_PERIOD = int(args.per_user_cooldown_count)

cooldown_start = 0
count_since_cooldown_start = 0

per_user_cooldown_start = {}
per_user_count_since_cooldown_start = {}

user_client = TelegramClient("frog_killer_session", api_id, api_hash)

foreign_shit_message_ids = dict()

yasru_filter = re.compile("#я[сc][рp][уy]", re.IGNORECASE)

nous_list = {
    "af": "Nee u",
    "sq": "Jo ju",
    "am": "አይ ዩ",
    "ar": "لا ش",
    "hy": "Ոչ դու",
    "az": "Yox u",
    "eu": "Ez u",
    "be": "Не ты",
    "bn": "না u",
    "bs": "No u",
    "bg": "Не ти",
    "ca": "No us",
    "ceb": "Dili u",
    "ny": "Ayi u",
    "zh-cn": "没有你",
    "zh-tw": "沒有你",
    "co": "No u",
    "hr": "Ne ti",
    "cs": "ne u",
    "da": "Nej u",
    "nl": "Nee jij",
    "en": "No u",
    "eo": "Ne u",
    "et": "Ei u",
    "tl": "hindi u",
    "fi": "Ei u",
    "fr": "Non toi",
    "fy": "Nei u",
    "gl": "Non u",
    "ka": "არა შენ",
    "de": "Nein u",
    "el": "Όχι εσύ",
    "gu": "ના યુ",
    "ht": "Non ou",
    "ha": "A'a ku",
    "haw": "ʻAʻole ʻoe",
    "iw": "לא אתה",
    "he": "לא אתה",
    "hi": "नहीं तुम",
    "hmn": "Tsis muaj u",
    "hu": "Nem u",
    "is": "Nei u",
    "ig": "Mba ị",
    "id": "Tidak kamu",
    "ga": "Níl u",
    "it": "No tu",
    "ja": "いいえ",
    "jw": "ora u",
    "kn": "ಇಲ್ಲ ಯು",
    "kk": "Жоқ сен",
    "km": "ទេអ្នក",
    "ko": "아니 유",
    "ku": "Na tu",
    "ky": "жок у",
    "lo": "ບໍ່",
    "la": "Non u *",
    "lv": "Nē u",
    "lt": "Ne u",
    "lb": "Nee u",
    "mk": "Не ти",
    "mg": "Tsia u",
    "ms": "Tidak u",
    "ml": "ഇല്ല യു",
    "mt": "Le u",
    "mi": "Kao u",
    "mr": "नाही यू",
    "mn": "Үгүй ээ",
    "my": "မဟုတ်ဘူးနော်။",
    "ne": "छैन यू",
    "no": "Nei u",
    "or": "ନା u",
    "ps": "نه یو",
    "fa": "نه تو",
    "pl": "Nie ty",
    "pt": "Não voce",
    "pa": "ਨਹੀਂ ਯੂ",
    "ro": "Nu tu",
    "ru": "нет ты",
    "sm": "Leai u",
    "gd": "Chan eil thu",
    "sr": "Не у",
    "st": "Che u",
    "sn": "Kwete u",
    "sd": "نه يو",
    "si": "නැහැ යූ",
    "sk": "Nie u",
    "sl": "Ne u",
    "so": "Maya u",
    "es": "No u",
    "su": "Henteu u",
    "sw": "Hapana u",
    "sv": "Nej du",
    "tg": "не у",
    "ta": "இல்லை யூ",
    "te": "లేదు యు",
    "th": "ไม่มีคุณ",
    "tr": "hayır sen",
    "uk": "Ні ти",
    "ur": "نہیں یو",
    "ug": "ياق",
    "uz": "Yo'q u",
    "vi": "Không bạn",
    "cy": "Na u",
    "xh": "Hayi wena",
    "yi": "ניין ו",
    "yo": "Rara o",
    "zu": "Cha u",
}
nos_list = [
    "no",
    "nei",
    "ne",
    "nay",
    "nah",
    "nö",
    "nein",
    "нет",
    "nope",
    "nop",
    "nada",
    "nah",
    "yox",
    "heyir",
    "hayir",
    "ba",
    "na",
    "ні",
    "не",
    "non"
]
yous_list = ["you", "u", "ye", "du", "ты", "sən", "sen", "tu", "ти", "thou", "toi"]
breaks_list = [",", ".", "-", " ", "\n", "!", "?", '"', "'", ";", ":", "_"]
digits_to_letters_map = {'0': 'o'}


def re_encode(strs):
    return list(map(lambda x: "(" + re.escape(x) + ")", strs))


breaks_list = re_encode(breaks_list)
breaks_regex = re.compile("[" + "".join(breaks_list) + "]")


def normalize(text):
    # lower case all
    text = text.lower()
    # remove the break chars
    text = breaks_regex.sub("", text)
    # map digits to letters just in case
    for (digit, letter) in digits_to_letters_map.items():
        text = text.replace(digit, letter)
    # collapse duplicates
    tmp_message_srt = ""
    last_c = ""
    for c in text:
        if c != last_c:
            tmp_message_srt += c
            last_c = c
    text = tmp_message_srt
    return text


def re_encode_normalize(strs):
    return list(map(lambda x: "(" + re.escape(normalize(x)) + ")", strs))


nous_list_norm = re_encode_normalize(list(nous_list.values()))
nos_list = re_encode_normalize(nos_list)
yous_list = re_encode_normalize(yous_list)

nous_regex = "|".join(nous_list_norm)
nos_regex = "|".join(nos_list)
yous_regex = "|".join(yous_list)
clean_str_regex = re.compile(
    "^(((" + nos_regex + ")(" + yous_regex + "))|(" + nous_regex + "))$"
)

cat_url = "https://some-random-api.ml/img/cat"


def is_nou(message_srt):
    # normalize string
    message_srt = normalize(message_srt)
    # test with regex
    return clean_str_regex.match(message_srt) is not None


@user_client.on(events.MessageDeleted())
async def handler(event):
    # Log all deleted message IDs
    for msg_id in event.deleted_ids:
        if msg_id in foreign_shit_message_ids:
            print("foreign_shit_message_ids:", msg_id, "was deleted in", event.chat_id)
            to_delete_msg = await user_client.get_messages(
                event.chat_id, ids=foreign_shit_message_ids[msg_id]
            )
            if to_delete_msg.message.lower() == "#йееей":
                print(
                    "foreign_shit_message_ids:",
                    msg_id,
                    "was deleted in",
                    event.chat_id,
                    "; confirmed text; del",
                )
                await user_client.delete_messages(
                    event.chat_id, [foreign_shit_message_ids.pop(msg_id)]
                )


def cooldown():
    global cooldown_start
    global count_since_cooldown_start

    print(f"GB: {cooldown_start}, {count_since_cooldown_start}")

    result = False

    if count_since_cooldown_start <= MAX_PER_COOLDOWN_PERIOD:
        count_since_cooldown_start += 1
        result = True

    if time.time() - cooldown_start > COOLDOWN_S:
        cooldown_start = time.time()
        count_since_cooldown_start = 0

    return result


def per_user_cooldown(user):
    if user is None:
        return False

    global per_user_cooldown_start
    global per_user_count_since_cooldown_start

    if user not in per_user_cooldown_start:
        per_user_cooldown_start[user] = 0
    if user not in per_user_count_since_cooldown_start:
        per_user_count_since_cooldown_start[user] = 0

    print(f"PU: {per_user_cooldown_start[user]}, {per_user_count_since_cooldown_start[user]}")

    result = False

    if per_user_count_since_cooldown_start[user] <= PER_USER_MAX_PER_COOLDOWN_PERIOD:
        per_user_count_since_cooldown_start[user] += 1
        result = True

    if time.time() - per_user_cooldown_start[user] > PER_USER_COOLDOWN_S:
        per_user_cooldown_start[user] = time.time()
        per_user_count_since_cooldown_start[user] = 0

    return result


@user_client.on(events.NewMessage())
async def handler(event):
    sender = await event.get_sender()

    if (
            yasru_filter.match(event.message.message.lower())
            and isinstance(sender, User)
            and not sender.is_self
    ):
        print("foreign shit event detected")
        # reply_msg = await event.reply('#йееей')
        # foreign_shit_message_ids[event.message.id] = reply_msg.id

    if (
            event.message.file is not None
            and event.message.file.mime_type == "video/webm"
            and event.message.file.emoji is None
            and (
            (
                    isinstance(sender, Channel)
                    and sender.admin_rights.post_messages
                    and sender.admin_rights.delete_messages
            )
            or (isinstance(sender, User) and sender.is_self)
    )
    ):
        print("webm self event detected")
        tmp_filename = "tmp" + str(random.random()) + ".webm"
        await user_client.download_file(event.message, file=tmp_filename)
        await user_client.delete_messages(
            entity=event.chat_id, message_ids=[event.message.id]
        )
        os.system(
            "ffmpeg -i " + tmp_filename + " -movflags faststart -pix_fmt yuv420p -vf"
                                          ' "scale=trunc(iw/2)*2:trunc(ih/2)*2" ' + tmp_filename + ".mp4"
        )
        await user_client.send_file(entity=event.chat_id, file=tmp_filename + ".mp4")
        os.remove(tmp_filename)
        os.remove(tmp_filename + ".mp4")

    if is_nou(event.message.message):
        if cooldown() and per_user_cooldown(sender.id):
            if not (
                    (
                            isinstance(sender, Channel)
                            and sender.admin_rights.post_messages
                            and sender.admin_rights.delete_messages
                    )
                    or (isinstance(sender, User) and sender.is_self)
            ):
                try:
                    lang = Translator().detect(text=event.message.message).lang
                except:
                    lang = "en"
                print(F"Detected a 'No u' from '{sender.username}'. Will reply in '{lang}'.")
                await event.reply(nous_list[lang])

    if event.message.message == "getPussy()":
        if cooldown() and per_user_cooldown((await event.get_sender()).id):
            cat_link = json.loads(requests.get(cat_url).text)["link"]
            filename = cat_link.split("/")[-1] + ".jpeg"
            r = requests.get(cat_link, stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                with open(filename, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
                await event.reply(file=filename)
                os.remove(filename)


async def user_main():
    await user_client.send_message("me", "Hello, myself!")


with user_client:
    user_client.loop.run_until_complete(user_main())
    user_client.run_until_disconnected()
