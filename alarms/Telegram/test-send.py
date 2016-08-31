# -*- coding: utf-8 -*-
import telepot
import telegram_stickers
import json
import os 
import sys

with open(os.path.abspath('../../locales/pokemon.en.json')) as file:
    stickerlist = json.load(file)




for k, v in telegram_stickers.sticker_list.iteritems():
#    print k + " " + v
    print stickerlist[k] + v
    # find the name for k	
