import unittest
import string

from GerryPasswordBot.password_generator.generator import PasswordGeneratorMixin, \
    AutomaticPasswordGeneration, CustomGenerationPassword


class TestPasswordGeneratorMixin(unittest.TestCase):
    """Проверить Миксин - PasswordGeneratorMixin."""
    def setUp(self):
        """Установить инстанс класса PasswordGeneratorMixin."""
        self.password = PasswordGeneratorMixin()

    def test_correct_sequence_length(self):
        """Проверить корректную длину сгенерированной последовательности."""
        correct_sequence_length = 6
        result = self.password.create_sequence()
        self.assertEqual(correct_sequence_length, len(result))

    def test_digit_in_sequence(self):
        """Проверить цифру в последовательности."""
        digit_in_sequence = False
        digits = tuple(string.digits)
        result = self.password.create_sequence()

        for symbol in result:
            if symbol in digits:
                digit_in_sequence = True
        self.assertTrue(digit_in_sequence)

    def test_sequence_is_string(self):
        """Последовательность является строкой."""
        result = self.password.create_sequence()
        self.assertIsInstance(result, str)


class TestAutomaticPasswordGeneration(unittest.TestCase):
    """Проверка класса автоматической генерации паролей."""

    def setUp(self):
        """Установить инстанс класса AutomaticPasswordGeneration."""
        self.password = AutomaticPasswordGeneration(auto_gen=True)

    def test_correct_length_password(self):
        """Пароль корректной длины = 20."""
        correct_password_length = 20
        result = self.password.generate_password()
        self.assertEqual(correct_password_length, len(result))

    def test_password_is_string(self):
        """Пароль является строкой."""
        result = self.password.generate_password()
        self.assertIsInstance(result, str)

    def test_password_contains_special_characters(self):
        """
        Пароль содержит 2 специальных знака: '-'.
        После split по специальным знакам, длина разделенного пароля
        должна равняться 3.
        """
        result = self.password.generate_password()
        password_without_special_characters = result.split('-')
        expected_number_of_elements = 3
        self.assertEqual(expected_number_of_elements,
                         len(password_without_special_characters))

    def test_incorrectly_initiated_class(self):
        """
        Вызывается исключение NameError, если неправильно инициирован класс.
        """
        with self.assertRaises(NameError) as error_message:
            password = AutomaticPasswordGeneration()
            password.generate_password()
        self.assertEqual(
            'Неправильно инициирован класс.', error_message.exception.args[0])


class TestCustomPasswordGeneration(unittest.TestCase):
    """Проверка класса кастомной генерации паролей."""

    def setUp(self) -> None:
        """
        Установить инстанс класса AutomaticPasswordGeneration с
        валидными данными.
        """
        self.correct_sequence = 'bYkzi9'
        self.incorrect_sequence = 'qigf~er'
        self.correct_password_length = 20
        self.user_sequence = 'kadabra'
        self.password = CustomGenerationPassword(
            password_length=self.correct_password_length,
            user_sequence=self.user_sequence)

    def test_sequence_with_correct_characters(self):
        """Проверить - корректность символов в последовательности."""
        expected_data = []
        result = self.password.check_for_invalid_characters_in_sequence(
            sequence=self.correct_sequence
        )
        self.assertEqual(expected_data, result)

    def test_sequence_with_invalid_characters(self):
        """Найти некорректный символ в последовательности."""
        expected_data = ['~']
        result = self.password.check_for_invalid_characters_in_sequence(
            sequence=self.incorrect_sequence
        )
        self.assertEqual(expected_data, result)

    def test_empty_character_in_sequence(self):
        """Найти в последовательности пустой символ."""
        expected_data = [' ']
        result = self.password.check_for_invalid_characters_in_sequence(
            sequence=' '
        )
        self.assertEqual(expected_data, result)

    def test_valid_number_of_characters_in_password(self):
        """Проверить валидное количество символов в пароле."""

        # 18 символов
        new_correct_sequence = self.correct_sequence * 3
        password = CustomGenerationPassword(
            password_length=len(new_correct_sequence),
            user_sequence=new_correct_sequence
        )
        self.assertTrue(password)

    def test_invalid_number_of_characters_in_password(self):
        """Проверить невалидное количество символов в пароле."""

        # 36 символов
        new_correct_sequence = self.correct_sequence * 6
        password = CustomGenerationPassword(
            password_length=len(new_correct_sequence),
            user_sequence=new_correct_sequence
        )
        with self.assertRaises(ValueError) as error_message:
            password.generate_password()
        self.assertEqual(
            'Длина пароля должна быть в интервале от 8 до 32',
            error_message.exception.args[0]
        )

    def test_lower_limit_on_number_of_characters_in_password(self):
        """Проверить нижнюю границу количества символов в пароле = 8."""
        new_correct_sequence = 'a' * 8
        password = CustomGenerationPassword(
            password_length=len(new_correct_sequence),
            user_sequence=new_correct_sequence
        )
        self.assertTrue(password)

    def test_upper_limit_on__number_of_characters_in_password(self):
        """Проверить верхнюю границу количества символов в пароле = 32."""
        new_correct_sequence = 'a' * 32
        password = CustomGenerationPassword(
            password_length=len(new_correct_sequence),
            user_sequence=new_correct_sequence
        )
        self.assertTrue(password)

    def test_user_entered_length_is_less(self):
        """Введенная пользователем длина пароля меньше."""
        length_from_user = 5
        password = CustomGenerationPassword(
            password_length=length_from_user,
            user_sequence=self.user_sequence
        )
        with self.assertRaises(ValueError) as error_message:
            password.generate_password()
        self.assertEqual(
            'Длина пароля должна быть в интервале от 8 до 32',
            error_message.exception.args[0]
        )

    def test_length_entered_by_user_is_greater(self):
        """Введенная пользователем длина пароля меньше."""
        length_from_user = 33
        password = CustomGenerationPassword(
            password_length=length_from_user,
            user_sequence=self.user_sequence
        )
        with self.assertRaises(ValueError) as error_message:
            password.generate_password()
        self.assertEqual(
            'Длина пароля должна быть в интервале от 8 до 32',
            error_message.exception.args[0]
        )

    def test_incorrect_sequence_from_user(self):
        """Проверить - некорректная последовательность от пользователя."""
        password = CustomGenerationPassword(
            password_length=self.correct_password_length,
            user_sequence=self.incorrect_sequence
        )
        with self.assertRaises(ValueError) as error_message:
            password.generate_password()
        self.assertEqual(
            "['~'] - недопустимые символы в последовательности.",
            error_message.exception.args[0]
        )

    def test_length_of_sequence_is_greater_total_length(self):
        """
        Проверить - введенная длина последовательности больше общей длины.
        """
        password = CustomGenerationPassword(
            password_length=9,
            user_sequence='wertfgyhju'
        )
        with self.assertRaises(ValueError) as error_message:
            password.generate_password()
        self.assertEqual(
            'Длина введенной последовательности больше общей длины пароля.',
            error_message.exception.args[0]
        )

    def test_find_cyrillic_in_user_sequence(self):
        """Найти кириллицу в последовательности от пользователя."""
        password = CustomGenerationPassword(
            password_length=self.correct_password_length,
            user_sequence='werПКsf'
        )
        with self.assertRaises(ValueError) as error_message:
            password.generate_password()
        self.assertEqual(
            'Недопустима последовательность содержащая кириллицу.',
            error_message.exception.args[0]
        )

    def test_correct_calculation_of_remaining_password_length(self):
        """Проверить - корректное вычисление оставшийся длины пароля."""
        expected_length = 13
        result = self.password.find_remaining_password_length()
        self.assertEqual(expected_length, result)

    def test_digit_in_sequence(self):
        """Цифра в последовательности."""
        result = self.password.check_for_numbers_in_sequence(
            sequence=self.correct_sequence)
        self.assertTrue(result)

    def test_no_digit_in_sequence(self):
        """Нет цифры в последовательности."""
        result = self.password.check_for_numbers_in_sequence(
            sequence=self.user_sequence
        )
        self.assertFalse(result)

    def test_generate_password_with_residual_length_of_one(self):
        """
        Сгенерировать пароль по остаточной длине = 1.
        Общая длина пароля = 8."""
        password = CustomGenerationPassword(
            password_length=8,
            user_sequence=self.user_sequence
        )
        expected_password_length = 8
        result = password.generate_password()
        self.assertEqual(expected_password_length, len(result))

    def test_generate_password_with_residual_length_of_two(self):
        """
        Сгенерировать пароль по остаточной длине = 2.
        Общая длина пароля = 9."""
        password = CustomGenerationPassword(
            password_length=9,
            user_sequence=self.user_sequence
        )
        expected_password_length = 9
        result = password.generate_password()
        self.assertEqual(expected_password_length, len(result))

    def test_generate_password_with_residual_length_of_three(self):
        """
        Сгенерировать пароль по остаточной длине = 3.
        Общая длина пароля = 10."""
        password = CustomGenerationPassword(
            password_length=10,
            user_sequence=self.user_sequence
        )
        expected_password_length = 10
        result = password.generate_password()
        self.assertEqual(expected_password_length, len(result))

    def test_generate_password_with_residual_length_greater_than_three(self):
        """
        Сгенерировать пароль по остаточной длине > 3.
        Общая длина пароля = 12."""
        password = CustomGenerationPassword(
            password_length=12,
            user_sequence=self.user_sequence
        )
        expected_password_length = 12
        result = password.generate_password()
        self.assertEqual(expected_password_length, len(result))

    def test_there_is_number_in_generated_password(self):
        """В сгенерированном пароле есть число."""
        result = self.password.generate_password()
        digits = list(string.digits)
        digit_in_sequence = any(
            map(lambda symbol: symbol in digits, result)
        )
        self.assertTrue(digit_in_sequence)

    def test_there_is_special_character_in_generated_password(self):
        """В сгенерированном пароле есть специальный знак."""
        special_sign = ['-']
        result = self.password.generate_password()
        special_character_in_sequence = any(
            map(lambda symbol: symbol in special_sign, result)
        )
        self.assertTrue(special_character_in_sequence)

    def test_password_is_generated_with_correct_total_length(self):
        """Генерируется пароль с корректной общей длиной."""
        expected_password_length = 18
        password = CustomGenerationPassword(
            password_length=18,
            user_sequence=self.user_sequence
        )
        result = password.generate_password()
        self.assertEqual(expected_password_length, len(result))


if __name__ == '__main__':
    unittest.main()
