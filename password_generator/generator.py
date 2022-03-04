import random
import string
from typing import List


class PasswordGeneratorMixin:
    """Миксин - генератор паролей."""

    @classmethod
    def create_sequence(cls) -> str:
        """Создать последовательность."""
        vowels = ('a', 'e', 'i', 'o', 'u', 'y')
        consonants = ('b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm',
                      'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z')
        random_digit = random.choice(tuple(string.digits))

        # генерируем полную последовательность из букв
        sequence = list()
        for _ in range(2):
            part_of_sequence = [
                random.choice(consonants) if index % 2 != 0 else random.choice(
                    vowels)
                for index in range(1, 4)
            ]
            sequence.extend(part_of_sequence)

        # заменяем одну рандомную букву на верхний регистр
        letter_from_sequence = random.choice(sequence)
        index_letter = sequence.index(letter_from_sequence)
        sequence[index_letter] = letter_from_sequence.upper()

        # заменяем в начале или на конце последовательности букву на цифру
        # 1 - в начало  2 - в конец
        choice = random.randrange(1, 3)
        if choice == 1:
            sequence[0] = random_digit
        elif choice == 2:
            sequence[len(sequence) - 1] = random_digit

        sequence_to_string = ''.join(sequence)
        return sequence_to_string


class AutomaticPasswordGeneration(PasswordGeneratorMixin):
    """
    Класс автоматической генерации полного пароля.

    Args:
        auto_gen (bool) = False: Инициализирует класс = True.
    """
    def __init__(self, auto_gen: bool = False) -> None:
        self.auto_gen = auto_gen

    def generate_password(self) -> str:
        """
        Сгенерировать полный пароль.

        Raises:
            NameError('Неправильно инициирован класс.'):
                Если неправильно инициирован класс.
        """
        if not self.__user_command_check():
            raise NameError('Неправильно инициирован класс.')

        password_by_parts = [
            self.create_sequence()
            for _ in range(3)
        ]
        ready_password = '-'.join(password_by_parts)
        return ready_password

    def __user_command_check(self) -> bool:
        """Проверить - пользователь выбрал автоматическую генерацию пароля."""
        if self.auto_gen is False:
            return False
        return True


class CustomGenerationPassword(PasswordGeneratorMixin):
    """
    Класс генерации пароля с учетом последовательности от пользователя.

    Args:
        password_length (int): Длина пароля пользователя.
        user_sequence (str): Последовательность пользователя.
    """
    def __init__(self, password_length: int, user_sequence: str) -> None:
        self.password_length = password_length
        self.user_sequence = user_sequence

    def generate_password(self) -> str:
        """
        Сгенерировать полный пароль с учетом последовательности от пользователя
        """
        random_letters = random.choice(string.ascii_lowercase)
        random_digit = random.choice(string.digits)
        ready_password = None

        # сформировать пароль в зависимости от остаточной длины
        if self.__general_validation_of_data_from_user():
            remaining_length = self.find_remaining_password_length()
            if remaining_length == 1:
                ready_password = '{0}{1}'.format(
                    self.user_sequence,
                    random_digit
                )
            elif remaining_length < 3:
                ready_password = '{0}{1}{2}'.format(
                    self.user_sequence,
                    random_letters,
                    random_digit
                )
            elif remaining_length == 3:
                ready_password = '{0}-{1}{2}'.format(
                    self.user_sequence,
                    random_letters,
                    random_digit
                )
            else:
                password_by_parts = [
                    self.create_sequence()
                    for _ in range(6)
                ]
                ready_password = '{0}-{1}'.format(
                    self.user_sequence,
                    '-'.join(password_by_parts)
                )[:self.password_length]

            if not self.check_for_numbers_in_sequence(sequence=ready_password):
                sequence_without_last_character = list(ready_password)
                sequence_without_last_character.pop()
                ready_password = '{0}{1}'.format(
                    ''.join(sequence_without_last_character),
                    random_digit
                )
        return ready_password

    def find_remaining_password_length(self):
        """Найти оставшуюся длину пароля."""
        remaining_length = self.password_length - len(self.user_sequence)
        return remaining_length

    @classmethod
    def check_for_invalid_characters_in_sequence(cls,
                                                 sequence: str) -> List[str]:
        """
        Проверить на недопустимые символы в последовательности.

        Args:
            sequence (str): Проверяемая последовательность.

        Returns:
            List[str]: Возвращается список :
                Пустой - если некорректные символы не найдены,
                С некорректными символами - если некорректные символы найдены.
        """
        char_whitespace = list(string.whitespace)
        invalid_characters = [
            '?', '#', '<', '>', '%', '@', '/', '\\', '~', '`', '"', ':',
        ]
        invalid_characters.extend(char_whitespace)

        found_invalid_characters = [
            symbol for symbol in sequence
            if symbol in invalid_characters
        ]
        return found_invalid_characters

    @classmethod
    def check_for_numbers_in_sequence(cls, sequence: str) -> bool:
        """
        Проверить наличие цифры в последовательности.

        Args:
            sequence (str): Последовательность для проверки.
        """
        digits = list(string.digits)
        digit_in_sequence = any(
            map(lambda symbol: symbol in digits, sequence)
        )
        return digit_in_sequence

    def __general_validation_of_data_from_user(self) -> bool:
        """Общая проверка на валидность данных от пользователя."""
        if not self.__check_number_of_characters_for_validity():
            raise ValueError(
                'Длина пароля должна быть в интервале от 8 до 32'
            )
        if not self.__check_incorrect_sequence_length_from_user():
            raise ValueError(
                'Длина введенной последовательности больше общей длины пароля.'
            )
        if not self.__check_sequence_for_cyrillic_characters():
            raise ValueError(
                'Недопустима последовательность содержащая кириллицу.'
            )
        invalid_characters = self.check_for_invalid_characters_in_sequence(
            sequence=self.user_sequence
        )
        if len(invalid_characters) > 0:
            raise ValueError(
                '{0} - недопустимые символы в последовательности.'.format(
                    invalid_characters
                )
            )
        return True

    def __check_number_of_characters_for_validity(self) -> bool:
        """Проверить количество символов на валидность."""
        minimum_length = 8
        maximum_length = 32
        if minimum_length <= self.password_length <= maximum_length:
            return True
        return False

    def __check_incorrect_sequence_length_from_user(self) -> bool:
        """Проверить - корректную длину введенной последовательности."""
        if len(self.user_sequence) > self.password_length:
            return False
        return True

    def __check_sequence_for_cyrillic_characters(self):
        """Проверить последовательность пользователя на символы кириллицы."""
        alphabet = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к",
                    "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц",
                    "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"]
        cyrillic_characters_in_sequence = any(
            map(lambda symbol: symbol.lower() in alphabet, self.user_sequence)
        )
        if cyrillic_characters_in_sequence:
            return False
        return True
