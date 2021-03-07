
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

class TelegramService():
    updater: Updater
    dispatcher: dispatcher
    token = "1692171028:AAF-1Z16YHRNIjaeOuhTdb6Q2-99TdYpYgg"

    __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

        self.updater = Updater(token=self.token, use_context=True)
        self.dispatcher = updater.dispatcher
        start_handler = CommandHandler('start', start)
        echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(echo_handler)

    def run(self):
        self.updater.start_polling()
    
    def stop(self):
        self.updater.stop()

    def start(update, context):
        context.bot.send_message(chat_id=self.update.effective_chat.id, text="I'm a bot, please talk to me!")

    def echo(update, context):
        context.bot.send_message(chat_id=self.update.effective_chat.id, text=self.update.message.text)
    
    def getOrders():
        return None
    
    def getPositions():
        return None
    
    def getPortfolio():
        return None