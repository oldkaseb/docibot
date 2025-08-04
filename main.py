from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import BOT_TOKEN
from handlers.start import start_handler
from handlers.message import user_message_handler, reply_message_handler, button_callback_handler
from handlers.admin import handlers as admin_handlers
from handlers.broadcast import forall_init_handler, handle_broadcast_message

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(start_handler)
    dp.add_handler(user_message_handler)
    dp.add_handler(reply_message_handler)
    dp.add_handler(button_callback_handler)
    dp.add_handler(forall_init_handler)
    dp.add_handler(MessageHandler(Filters.private & ~Filters.command, handle_broadcast_message))
    
    for handler in admin_handlers:
        dp.add_handler(handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
