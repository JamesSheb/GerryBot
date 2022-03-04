import os

import telebot
from telebot import types
from loguru import logger


from gerry_bot_config import BOT_TOKEN
from password_generator import AutomaticPasswordGeneration, \
    CustomGenerationPassword


logger.add('logs/bot.log',
           format="{time:YYYY-MM-DD at HH:mm:ss} {file} (line - {line})  {level}  {message} <- {function} ",
           level='DEBUG',
           rotation='1 week',
           retention=4,
           compression='zip')

# TODO: написать файл README
# TODO: добавить в гитигнор файлы:
#     - env
#     - папку всю с логами

bot = None
try:
    bot = telebot.TeleBot(token=BOT_TOKEN)
except Exception as bot_error:
    logger.exception(bot_error)


@logger.catch
@bot.message_handler(commands=['start'])
def start_message(message: types.Message) -> None:
    """Начать стартовый диалог с пользователем."""
    hello_messages = 'Hello, {0}\nМеня зовут Gerry Password.\n\n' \
                     'Я подберу для вас пароль!\n' \
                     'В автоматическом или кастомном режиме.'.format(
                        message.from_user.first_name)
    buttons_message = 'Выберите и нажмите на более предпочтительный'
    try:
        path_to_sticker = os.path.abspath(
            os.path.join('', 'static/stickers/HelloAnimatedSticker.tgs'))
        sticker = open(path_to_sticker, mode='rb')
    except FileNotFoundError:
        sticker = '👋'

    markup = types.InlineKeyboardMarkup()
    automatic_selection = types.InlineKeyboardButton(
                                                'Автоматический',
                                                callback_data='auto_gen')
    custom_selection = types.InlineKeyboardButton(
                                                'Кастомный',
                                                callback_data='custom_gen')
    markup.add(automatic_selection, custom_selection)

    try:
        bot.send_sticker(message.chat.id, sticker)
    except Exception as error_message:
        logger.exception('Ошибка загрузки стикера "hello" - {0}'.format(
                                                                error_message))
        bot.send_message(message.chat.id, sticker)
    bot.send_message(message.chat.id, hello_messages)
    bot.send_message(message.chat.id, buttons_message, reply_markup=markup)


@logger.catch
@bot.callback_query_handler(func=lambda call: call.data == 'auto_gen')
def callback_automatic_password_generation(call: types.CallbackQuery) -> None:
    """Обработать автоматическую генерацию пароля."""
    logger.debug('Выбрана автоматическая генерация пароля пользователем')
    password = None
    if call.data == 'auto_gen':
        generation = AutomaticPasswordGeneration(auto_gen=True)
        password = generation.generate_password()

    markup = user_password_answer_buttons(automatic_selection=True)

    # заменить предыдущее сообщение
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Ваш пароль:\n\n{0}'.format(password),
                          reply_markup=markup)


@logger.catch
@bot.callback_query_handler(func=lambda call: call.data == 'custom_gen')
def callback_custom_password_generation(call: types.CallbackQuery) -> None:
    """Обработать генерацию пользовательского пароля."""
    logger.debug('Выбрана кастомная генерация пароля пользователем')
    if call.data == 'custom_gen':
        chat_message = bot.send_message(
            chat_id=call.message.chat.id,
            text='Введите введите общую длину пароля от 8 до 32 '
                 '(включительно).')
        bot.register_next_step_handler(chat_message,
                                       password_length_from_user)


@logger.catch
def password_length_from_user(message: types.Message) -> None:
    """Получить от пользователя общую длину пароля."""
    password_length = None
    try:
        password_length = int(message.text)
    except ValueError as error_message:
        logger.exception('Ошибка ввода от пользователя - {0}'.format(
                                                                error_message))
        chat_message = bot.send_message(
                                message.chat.id,
                                'Введите пожалуйста цифрами.')
        bot.register_next_step_handler(chat_message, password_length_from_user)

    if password_length:
        chat_message = bot.send_message(
            chat_id=message.chat.id,
            text='Введите последовательность не превышающую'
                 ' общую длину пароля.\n'
                 'Например - (любимый бренд или марка вашего авто)\n\n'
                 'Пароль должен содержать латинские буквы и/или цифры.'
        )
        bot.register_next_step_handler(chat_message,
                                       generate_custom_password_for_user,
                                       password_length)


@logger.catch
def generate_custom_password_for_user(message: types.Message,
                                      password_length: int) -> None:
    """
    Получить общую длину пароля и последовательность от пользователя.

    Args:
        message: class Message.
        password_length (int): Длина пароля от пользователя.
    """
    user_password_length = password_length
    user_sequence = message.text
    ready_password = None

    logger.info(
        'Введенная длина - "{0}", последовательность - "{1}"'
        ' от пользователя'.format(user_password_length, user_sequence))
    generation = CustomGenerationPassword(
        password_length=user_password_length,
        user_sequence=user_sequence
    )
    try:
        ready_password = generation.generate_password()
    except ValueError as error_message:
        logger.warning('Ошибка ввода от пользователя - {0}'.format(
                                                                error_message))
        markup = types.InlineKeyboardMarkup()
        custom_selection = types.InlineKeyboardButton(
                                                'Ввести данные заново',
                                                callback_data='custom_gen')
        markup.add(custom_selection)

        bot.send_message(message.chat.id, str(error_message),
                         reply_markup=markup)

    if ready_password:
        markup = user_password_answer_buttons(custom_selection=True)

        bot.send_message(message.chat.id,
                         text='Ваш пароль:\n\n{0}'.format(ready_password),
                         reply_markup=markup)


@logger.catch
def user_password_answer_buttons(
        automatic_selection: bool = False,
        custom_selection: bool = False) -> 'types.InlineKeyboardMarkup':
    """
    Создать клавиатуру с кнопками: 'OK' и 'Повтор генерации'.
    Кнопка 'Повтор генерации':
        меняется callback_data в зависимости от выбора:
        auto = True или custom = True

    Args:
        automatic_selection (bool) = False: Если = True создаются кнопки
            для автоматической генерации пароля.
        custom_selection (bool) = False: Если = True создаются кнопки
            для кастомной генерации пароля.

    Returns:
         Класс 'InlineKeyboardMarkup' с 2-мя кнопками.
    """
    markup = types.InlineKeyboardMarkup()
    ok_selection = types.InlineKeyboardButton('OK!',
                                              callback_data='ok_selection')
    repeat_automatic_selection = types.InlineKeyboardButton(
                                        'Повтор генерации',
                                        callback_data='auto_gen')
    repeat_custom_selection = types.InlineKeyboardButton(
                                        'Повтор генерации',
                                        callback_data='custom_gen')
    if automatic_selection:
        markup.add(ok_selection, repeat_automatic_selection)
    elif custom_selection:
        markup.add(ok_selection, repeat_custom_selection)
    return markup


@logger.catch
@bot.callback_query_handler(func=lambda call: call.data == 'ok_selection')
def callback_user_decision_is_ok(call: types.CallbackQuery) -> None:
    """Обработать кнопку == ok_selection."""
    if call.data == 'ok_selection':
        ok_message = '*{0}*\n\nКлассный выбор!'.format(call.message.text)
        try:
            path_to_sticker = os.path.abspath(
                os.path.join(
                    '', 'static/stickers/EndAnimatedSticker.tgs'))
            sticker = open(path_to_sticker, mode='rb')
        except FileNotFoundError:
            sticker = '😎'
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=ok_message,
                              reply_markup=None,
                              parse_mode='Markdown')
        try:
            bot.send_sticker(call.message.chat.id, sticker)
        except Exception as error_message:
            logger.exception('Ошибка загрузки стикера "end" - {0}'.format(
                                                                error_message))
            bot.send_message(call.message.chat.id, sticker)


@logger.catch
@bot.message_handler(content_types=['text'])
def process_all_messages_from_user(message: types.Message) -> None:
    """Обработать сообщения от пользователя и перенаправить на start."""
    if message.text != '/start':
        bot.send_message(chat_id=message.chat.id,
                         text='Для генерации пароля введите - /start')


if __name__ == '__main__':
    try:
        logger.debug('Start bot')
        bot.polling(none_stop=True, interval=0)
    except Exception as error:
        logger.exception(error)
