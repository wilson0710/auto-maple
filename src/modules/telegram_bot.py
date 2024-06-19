#Header imports
# import telegram
# from telegram.ext import *

#Change this only
API_KEY     = '7201268008:AAFBQ9qu22WTljqjVmGSnYIGK73_GwYl9aA'
CHAT_ID     = '-4001872274'

#Do not touch the rest
BASE_URL    = 'https://api.telegram.org/bot' + API_KEY + '/sendMessage?chat_id='+ CHAT_ID

receive_info    = True
receive_warning = True

"""Message Senders"""
def send_info_msg(message):
    if receive_info:
        import requests
        final_message =  BASE_URL + '&text=' + '[Info] ' + message
        # print(final_message)
        requests.get(final_message)

def send_warning_msg(message):
    if receive_warning:
        import requests
        final_message =  BASE_URL + '&text=' + '[Warning] ' + message
        # print(final_message)
        requests.get(final_message)

# """Notification"""

# #All
# def mute_all_command(update, context):
#     receive_info = receive_warning = False
#     update.message.reply_text('All notification has been muted')
    
# def unmute_all_command(update, context):
#     receive_info = receive_warning = True
#     update.message.reply_text('All notification has been unmuted')

# #Info
# def mute_info_command(update, context):
#     receive_info = False
#     update.message.reply_text('All [Info] notification has been muted')
    
# def unmute_info_command(update, context):
#     receive_info = True
#     update.message.reply_text('All [Info] notification has been unmuted')

# #Warning
# def mute_warning_command(update, context):
#     receive_warning = False
#     update.message.reply_text('All [Warning] notification has been muted')
    
# def unmute_warning_command(update, context):
#     receive_warning = True
#     update.message.reply_text('All [Warning] notification has been unmuted')


# def start():
#     # bot = telegram.Bot(token='[REMOVED BOT TOKEN BUT CAN CONFIRM IT'S CORRECT]')(token='[REMOVED BOT TOKEN BUT CAN CONFIRM IT'S CORRECT]')
    
#     application = Application.builder().token(API_KEY).build()
#     # updater = Updater(API_KEY, update_queue)
#     # dp = updater.dispatcher

#     application.add_handler(CommandHandler("muteall", mute_all_command))
#     application.add_handler(CommandHandler("unmuteall", unmute_all_command))

#     application.add_handler(CommandHandler("muteinfo", mute_info_command))
#     application.add_handler(CommandHandler("muteinfo", unmute_info_command))

#     application.add_handler(CommandHandler("mutewarning", mute_warning_command))
#     application.add_handler(CommandHandler("mutewarning", unmute_warning_command))

#     application.start_polling()
#     application.idle()

    