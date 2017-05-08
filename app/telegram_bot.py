import os

from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
import logging
import configparser
from app.artifactory_frog_api import ArtifactsFrog

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
frog = ArtifactsFrog()

get_config_file = lambda mode_name: './config/main.{mode_name}.ini'.format(mode_name=mode_name)
print(get_config_file('local'))

config = configparser.ConfigParser()
config.sections()
if os.path.isfile(get_config_file('local')):
    config.read(get_config_file('local'))
else:
    config.read(get_config_file('production'))


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="I'm your little helper!")


def echo(bot, update):
    """
    handler that listens for regular messages
    :param bot:
    :param update:
    """
    bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)


def caps(bot, update, args):
    text_caps = ' '.join(args).upper()
    bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)


USER, PASSWORD = range(2)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('%s - %s' % (key, value))

    return "\n".join(facts).join(['\n', '\n'])


def print_builds(bot, update):
    text = "\n".join(str(item) for item in frog.get_repo_content())
    bot.sendMessage(chat_id=update.message.chat_id, text=text)


def download_version(bot, update, user_data, args):
    if len(args) > 0:
        user_data['version'] = args[0]
    else:
        user_data['version'] = None
    bot.sendMessage(chat_id=update.message.chat_id, text='Send me user-name')
    return USER


def auth_user(bot, update, user_data):
    user_data['user'] = update.message.text
    bot.sendMessage(chat_id=update.message.chat_id, text='Send me password')
    return PASSWORD


def get_version(user_data):
    if 'version' in user_data:
        return user_data['version']
    return None


def get_user(user_data):
    if 'user' in user_data:
        return user_data['user']
    return None


def get_password(user_data):
    if 'password' in user_data:
        return user_data['password']
    return None


def auth_password(bot, update, user_data):
    user_data['password'] = update.message.text
    bot.sendMessage(chat_id=update.message.chat_id,
                    text='Thanks, {user_data}'.format(user_data=facts_to_str(user_data)))
    download(bot, update, user_data)
    return ConversationHandler.END


def download(bot, update, user_data):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text='starting download')
    frog = ArtifactsFrog(user=get_user(user_data), password=get_password(user_data))
    send_msg_to_user = lambda msg: bot.sendMessage(chat_id=update.message.chat_id, text=msg)
    frog.download_build(build_name=get_version(user_data), print_callback=send_msg_to_user)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text='Download completed')


def help(bot, update):
    text = '\n'
    for handler in handlers:
        if type(handler) is CommandHandler:
            command_name = handler.command
        elif type(handler) is ConversationHandler:
            command_name = handler.entry_points[0].command
        else:
            command_name = ''
        text += command_name + '\n'
    bot.sendMessage(chat_id=update.message.chat_id, text=text)


def unknown(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def cancel(bot, update, user_data):
    user = update.message.from_user
    logger.info("User %s canceled the conversation." % user.first_name)
    download(bot, update, user_data)
    return ConversationHandler.END


handlers = [
    CommandHandler('start', start),
    CommandHandler('caps', caps, pass_args=True),  # test handler
    ConversationHandler(
        entry_points=[CommandHandler('download_build', download_version, pass_args=True, pass_user_data=True)],
        states={
            USER: [MessageHandler(Filters.text, auth_user, pass_user_data=True)],
            PASSWORD: [MessageHandler(Filters.text, auth_password, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]),
    CommandHandler('print_builds', print_builds),
    CommandHandler('help', help),
    MessageHandler(Filters.text, echo),
    MessageHandler(Filters.command, unknown)  # must be added last
]


def main():
    updater = Updater(token=config.get('TELEGRAM', 'token'))
    dispatcher = updater.dispatcher

    for handler in handlers:
        dispatcher.add_handler(handler)

    # log all errors
    dispatcher.add_error_handler(error)
    # start the bot
    updater.start_polling()

    # Block until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
