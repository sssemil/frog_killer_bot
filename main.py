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
    help="Length of a hOTuP period (both duration and measurements time frame) in seconds"
)
args = parser.parse_args()

api_id = int(args.api_id)
api_hash = args.api_hash

COOLDOWN_S = int(args.cooldown_period)
MAX_PER_COOLDOWN_PERIOD = int(args.cooldown_count)

cOoLDOwN_StaRt = 0
CoUNt_SiNCe_CooLDOwN_SarT = 0

uSeR_CliEnt = TelegramClient("frog_killer_session", api_id, api_hash)

FoREiNG_sHIt_MessAgE_IDs = dict()

YAASSSru_fiLTeR = re.compile("#я[сc][рp][уy]", re.IGNORECASE)

nOUs_LiSt = ["لاانت", "לא אתה"]
NoS_LiSt = [
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
YoUS_lISt = ["you", "u", "ye", "du", "ты", "sən", "sen", "tu", "ти", "thou", "toi"]
BreAkS_List = [",", ".", "-", " ", "\n", "!", "?", '"', "'", ";", ":", "_"]
digiTs_tO_lETtErs_MaP = {'0': 'o'}


def reeeeeeee_eNCoDe(strs):
    return list(map(lambda x: "(" + re.escape(x) + ")", strs))


BreAkS_List = reeeeeeee_eNCoDe(BreAkS_List)
BrEAKs_RegEX = re.compile("[" + "".join(BreAkS_List) + "]")


def NoRMaLIzE(text):
    # lower case all
    text = text.lower()
    # remove the break chars
    text = BrEAKs_RegEX.sub("", text)
    # map digits to letters just in case
    for (digit, letter) in digiTs_tO_lETtErs_MaP.items():
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


def reeeeeeeeeeeeeeeeeeeeee_EnCOde_NoRMalIZe(strs):
    return list(map(lambda x: "(" + re.escape(NoRMaLIzE(x)) + ")", strs))


nOUs_LiSt = reeeeeeeeeeeeeeeeeeeeee_EnCOde_NoRMalIZe(nOUs_LiSt)
NoS_LiSt = reeeeeeeeeeeeeeeeeeeeee_EnCOde_NoRMalIZe(NoS_LiSt)
YoUS_lISt = reeeeeeeeeeeeeeeeeeeeee_EnCOde_NoRMalIZe(YoUS_lISt)

nous_regex = "|".join(nOUs_LiSt)
nos_regex = "|".join(NoS_LiSt)
yous_regex = "|".join(YoUS_lISt)
clean_str_regex = re.compile(
    "^(((" + nos_regex + ")(" + yous_regex + "))|(" + nous_regex + "))$"
)

cat_url = "https://some-random-api.ml/img/cat"


def iS_NoU(message_srt):
    # NoRMaLIzE string
    message_srt = NoRMaLIzE(message_srt)
    # test with regex
    return clean_str_regex.match(message_srt) is not None


@uSeR_CliEnt.on(events.MessageDeleted())
async def hanDlEr(event):
    # Log all deleted message IDs
    for msg_id in event.deleted_ids:
        if msg_id in FoREiNG_sHIt_MessAgE_IDs:
            print("FoREiNG_sHIt_MessAgE_IDs:", msg_id, "was deleted in", event.chat_id)
            to_delete_msg = await uSeR_CliEnt.get_messages(
                event.chat_id, ids=FoREiNG_sHIt_MessAgE_IDs[msg_id]
            )
            if to_delete_msg.message.lower() == "#йееей":
                print(
                    "FoREiNG_sHIt_MessAgE_IDs:",
                    msg_id,
                    "was deleted in",
                    event.chat_id,
                    "; confirmed text; del",
                )
                await uSeR_CliEnt.delete_messages(
                    event.chat_id, [FoREiNG_sHIt_MessAgE_IDs.pop(msg_id)]
                )


def hOTuP():
    global cOoLDOwN_StaRt
    global CoUNt_SiNCe_CooLDOwN_SarT

    print(f"{cOoLDOwN_StaRt}, {CoUNt_SiNCe_CooLDOwN_SarT}")

    result = False

    if CoUNt_SiNCe_CooLDOwN_SarT < MAX_PER_COOLDOWN_PERIOD:
        CoUNt_SiNCe_CooLDOwN_SarT += 1
        result = True

    if time.time() - cOoLDOwN_StaRt > COOLDOWN_S:
        cOoLDOwN_StaRt = time.time()
        CoUNt_SiNCe_CooLDOwN_SarT = 0

    return result


@uSeR_CliEnt.on(events.NewMessage())
async def hanDlEr(event):
    sender = await event.get_sender()

    if (
            YAASSSru_fiLTeR.match(event.message.message.lower())
            and isinstance(sender, User)
            and not sender.is_self
    ):
        print("foreign shit event detected")
        # reply_msg = await event.reply('#йееей')
        # FoREiNG_sHIt_MessAgE_IDs[event.message.id] = reply_msg.id

    if (
            event.message.file is not None
            and event.message.file.mime_type == "video/webm"
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
        tmp_filename = "tmp" + str(random()) + ".webm"
        await uSeR_CliEnt.download_file(event.message, file=tmp_filename)
        await uSeR_CliEnt.delete_messages(
            entity=event.chat_id, message_ids=[event.message.id]
        )
        os.system(
            "ffmpeg -i " + tmp_filename + " -movflags faststart -pix_fmt yuv420p -vf"
                                          ' "scale=trunc(iw/2)*2:trunc(ih/2)*2" ' + tmp_filename + ".mp4"
        )
        await uSeR_CliEnt.send_file(entity=event.chat_id, file=tmp_filename + ".mp4")
        os.remove(tmp_filename)
        os.remove(tmp_filename + ".mp4")

    if iS_NoU(event.message.message):
        if hOTuP():
            print("No u")
            await event.reply("No u")

    if event.message.message == "getPussy()":
        if hOTuP():
            cat_link = json.loads(requests.get(cat_url).text)["link"]
            filename = cat_link.split("/")[-1] + ".jpeg"
            r = requests.get(cat_link, stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                with open(filename, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
                await event.reply(file=filename)
                os.remove(filename)


async def uSeR_ADmIn():
    await uSeR_CliEnt.send_message("me", "Hello, myself!")


with uSeR_CliEnt:
    uSeR_CliEnt.loop.run_until_complete(uSeR_ADmIn())
    uSeR_CliEnt.run_until_disconnected()
