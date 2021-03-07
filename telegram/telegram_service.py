
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

class TelegramService():
    updater: Updater
    dispatcher: dispatcher
    token = "1692171028:AAF-1Z16YHRNIjaeOuhTdb6Q2-99TdYpYgg"

    __init__(self):
        self.updater = Updater(token=self.token, use_context=True)
        self.dispatcher = updater.dispatcher
        start_handler = CommandHandler('start', start)
        dispatcher.add_handler(CommandHandler('bad_command', bad_command))
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(echo_handler)

    def run(self):
        self.updater.start_polling()
        self.updater.idle()
    
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

    def bad_command(update: Update, context: CallbackContext) -> None:
    """Raise an error to trigger the error handler."""
    context.bot.wrong_method_name()

    def error_handler(update: Update, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)