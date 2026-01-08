from enum import StrEnum


class EnglishLevel(StrEnum):
    BEGINNER = 'beginner'
    ELEMENTARY = 'elementary'
    INTERMEDIATE = 'intermediate'
    UPPER_INTERMEDIATE = 'upper intermediate'
    ADVANCED = 'advanced'


class EnglishReadingQuestionType(StrEnum):
    MULTIPLE_CHOICE = "multiple_choice"  # Классика
    FILL_GAP = "fill_gap"
    MATCHING = "matching"  # Соединить пары (Формулы, Синонимы)
    ORDERING = "ordering"
    FIND_ERROR = "find_error"  # Тапнуть на ошибку в тексте
    STRIKE_OUT = "strike_out"  # Вычеркнуть лишнее (Redundancy questions)
    HIGHLIGHT = "highlight"


class MathScienceQuestionType(StrEnum):
    MULTIPLE_CHOICE = "multiple_choice"  # Классика
    FILL_GAP = "fill_gap"
    MATCHING = "matching"  # Соединить пары (Формулы, Синонимы)
    ORDERING = "ordering"
    GRAPH_POINT = "graph_point"  # Тапнуть в нужную точку графика
    SWIPE_DECISION = "swipe_decision"  # Свайп влево/вправо (Fact/Opinion, Correct/Incorrect)
    SLIDER_VALUE = "slider_value"  # Подобрать значение ползунком (Оценка значений)


class QuestionType(StrEnum):
    # --- Универсальные (Common) ---
    MULTIPLE_CHOICE = "multiple_choice"  # Классика с таймером
    FILL_GAP = "fill_gap"  # Ввод слова или числа
    MATCHING = "matching"  # Соединить пары
    ORDERING = "ordering"  # Расставить по порядку

    # --- English & Reading ---
    FIND_ERROR = "find_error"  # Тапнуть на ошибку
    STRIKE_OUT = "strike_out"  # Вычеркнуть лишнее
    HIGHLIGHT = "highlight"  # Выделить текст

    # --- Math & Science ---
    GRAPH_POINT = "graph_point"  # Тапнуть точку на графике
    SWIPE_DECISION = "swipe_decision"  # Свайп (Да/Нет, Факт/Мнение)
    SLIDER_VALUE = "slider_value"  # Ползунок значения
    TREND_ARROW = "trend_arrow"  # Выбрать направление тренда (⬆️⬇️)


class FundType(StrEnum):
    COIN = "coin"
    CRYSTAL = "crystal"


class SubjectEnum(StrEnum):
    ENGLISH = "english"
    READING = "reading"
    SCIENCE = "science"
    MATH = "math"