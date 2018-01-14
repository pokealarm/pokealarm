# -*- coding: utf-8 -*-
import telepot
from telepot.loop import MessageLoop
import json


class ConfiguratorBot(telepot.helper.ChatHandler):
    bot = None

    def __init__(self, token, log):
        self.bot = telepot.Bot(token)
        MessageLoop(self.bot, self.handle).run_as_thread()
        log.info("Listening for Filters configurations")

        # Keep the program running.

    def loadFilters(self):
        with open("filters.json", 'r') as f:
            return json.load(f)

    def saveFilters(self, filters):
        with open("filters.json", 'w') as f:
            json.dump(filters, f)

    def handle(self, msg):
        chat_id = msg['chat']['id']
        query_data = msg['text']

        words = query_data.split(" ")

        if words[0].lower() == "remove":
            if words[1].lower() == "raid":
                filters = self.loadFilters()
                if words[2].title() in filters["raids"]["filters"]["filter-name"]["monsters"]:
                    filters["raids"]["filters"]["filter-name"]["monsters"].remove(
                        words[2].title())

                    self.saveFilters(filters)
                    self.bot.sendMessage(chat_id, 'Raid successfully removed.')
                else:
                    self.bot.sendMessage(chat_id, 'Raid not found.')

            elif words[1].lower() == "pokemon" or words[1].lower() == "pokémon":
                filters = self.loadFilters()
                if words[2].title() in filters["raids"]["filters"]["filter-name"]["monsters"]:
                    filters["monsters"]["filters"]["filter-name"]["monsters"].remove(
                        words[2].title())

                    self.saveFilters(filters)
                    self.bot.sendMessage(
                        chat_id, 'Pokémon successfully removed.')
                else:
                    self.bot.sendMessage(chat_id, 'Pokémon not found.')
            else:
                self.bot.sendMessage(
                    chat_id, 'Type of alert that does not exist')

        elif words[0].lower() == "add":
            if words[1].lower() == "raid":
                filters = self.loadFilters()

                if words[2].title() in filters["raids"]["filters"]["filter-name"]["monsters"]:
                    self.bot.sendMessage(chat_id, 'Raid already registered.')
                else:
                    filters["raids"]["filters"]["filter-name"]["monsters"].append(
                        words[2].title())

                    self.saveFilters(filters)
                    self.bot.sendMessage(
                        chat_id, 'Raid successfully registered.')

            elif words[1].lower() == "pokemon" or words[1].lower() == "pokémon":
                filters = self.loadFilters()

                if words[2].title() in filters["raids"]["filters"]["filter-name"]["monsters"]:
                    self.bot.sendMessage(
                        chat_id, 'Pokémon already registered.')
                else:
                    filters["monsters"]["filters"]["filter-name"]["monsters"].append(
                        words[2].title())

                    self.saveFilters(filters)
                    self.bot.sendMessage(
                        chat_id, 'Pokémon successfully registered.')
            else:
                self.bot.sendMessage(
                    chat_id, 'Type of alert that does not exist.')
        else:
            self.bot.sendMessage(chat_id, 'Unknown command.')
