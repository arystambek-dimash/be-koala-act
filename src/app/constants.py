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


# Уровень: Сколько XP нужно, чтобы перейти на СЛЕДУЮЩИЙ
LEVEL_TABLE = {
    1: 500,  # Чтобы перейти с 1 на 2 нужно 500
    2: 1000,  # Чтобы перейти с 2 на 3 нужно 1000
    3: 2000,
    4: 5000,
    5: 10000,  # Максимальный порог, как ты хотел
}

MAX_LEVEL = 5


class BuildingType(StrEnum):
    VILLAGE = "village"
    CASTLE = "castle"


PROMPTS = {
    # =========================================================================
    # ENGLISH (Грамматика, Пунктуация, Стиль)
    # Используем: FIND_ERROR, STRIKE_OUT, ORDERING, MULTIPLE_CHOICE
    # =========================================================================
    "english": """
        You are an expert ACT English Tutor.
        Generate a strictly valid JSON response with practice questions.

        ### CONTEXT:
        - Topic: {topic}
        - Description: {description}
        - Level: {level}

        ### QUESTION TYPES (Strictly use these keys):

        1. TYPE: "find_error"
           Description: The user must tap the single word that contains a grammatical error.
           JSON Structure:
           {
             "type": "find_error",
             "text": "Find the grammatical error.",
             "content": {
               "sentence": "The committee have reached a decision.", 
               "error_index": 2,  // Index of the word 'have' (0-based)
               "correct_word": "has",
               "explanation": "'Committee' is singular here."
             }
           }

        2. TYPE: "strike_out"
           Description: The user must remove redundant or unnecessary words.
           JSON Structure:
           {
             "type": "strike_out",
             "text": "Remove the redundant text.",
             "content": {
               "sentence": "The wet rain fell down from the sky.",
               // The frontend will split this string by spaces. 
               // Indices to remove: 'wet' (1) and 'from the sky' (5,6,7)
               "correct_ids_to_remove": [1, 5, 6, 7], 
               "explanation": "'Rain' is always wet, and falls from the sky."
             }
           }

        3. TYPE: "ordering"
           Description: Arrange words/phrases to form a correct sentence.
           JSON Structure:
           {
             "type": "ordering",
             "text": "Arrange the sentence correctly.",
             "content": {
               "items": [
                 {"id": "1", "content": "Walking down the street,"}, 
                 {"id": "2", "content": "the trees"},
                 {"id": "3", "content": "looked beautiful."}
               ],
               "correct_order": ["1", "3", "2"], // Logic check
               "explanation": "Modifier placement rule."
             }
           }
    """,

    # =========================================================================
    # READING (Понимание текста)
    # Используем: HIGHLIGHT, MULTIPLE_CHOICE, SWIPE_DECISION, ORDERING
    # =========================================================================
    "reading": """
        You are an expert ACT Reading Tutor.
        Generate a strictly valid JSON response based on a generated short passage.

        ### CONTEXT:
        - Topic: {topic} (Generate a 3-4 sentence passage based on this)
        - Level: {level}

        ### QUESTION TYPES (Strictly use these keys):

        1. TYPE: "highlight"
           Description: The user must highlight the exact phrase that answers the question.
           JSON Structure:
           {
             "type": "highlight",
             "text": "Highlight the evidence.",
             "content": {
               "passage": "Full passage text goes here...",
               "question": "What specifically caused the character's anger?",
               "correct_phrase": "the broken vase", // Must exist exactly in passage
               "explanation": "The text explicitly states the vase caused the anger."
             }
           }

        2. TYPE: "swipe_decision"
           Description: Decide if a statement is Fact or Opinion (or True/False).
           JSON Structure:
           {
             "type": "swipe_decision",
             "text": "Is this Fact or Opinion?",
             "content": {
               "cards": [
                 {
                    "content": "The author suggests that whales are majestic.", 
                    "correct_swipe": "right", 
                    "explanation": "Majestic is subjective."
                 },
                 {
                    "content": "Whales are mammals.", 
                    "correct_swipe": "left", 
                    "explanation": "This is a biological fact."
                 }
               ],
               "labels": {"left": "Fact", "right": "Opinion"}
             }
           }

        3. TYPE: "multiple_choice"
           Description: Standard reading comprehension.
           JSON Structure:
           {
             "type": "multiple_choice",
             "text": "Main Idea",
             "content": {
               "question": "What is the main theme?",
               "options": [
                 {"id": "a", "text": "Nature vs Nurture", "is_correct": true},
                 {"id": "b", "text": "Technology", "is_correct": false}
               ],
               "explanation": "..."
             }
           }
    """,

    # =========================================================================
    # MATH (Алгебра, Геометрия)
    # Используем: FILL_GAP, MATCHING, ORDERING, GRAPH_POINT, MULTIPLE_CHOICE
    # =========================================================================
    "math": """
        You are an expert ACT Math Tutor. 
        Use LaTeX for all math expressions (wrapped in $...$).

        ### CONTEXT:
        - Topic: {topic}
        - Level: {level}

        ### QUESTION TYPES (Strictly use these keys):

        1. TYPE: "fill_gap"
           Description: Solve the equation.
           JSON Structure:
           {
             "type": "fill_gap",
             "text": "Solve for x.",
             "content": {
               "question": "If $2x + 10 = 20$, then $x = ?$",
               "correct_answer": "5",
               "explanation": "Subtract 10, then divide by 2."
             }
           }

        2. TYPE: "matching"
           Description: Match formula to name or expression to value.
           JSON Structure:
           {
             "type": "matching",
             "text": "Match the equivalents.",
             "content": {
               "pairs": [
                 {"id": "1", "left": "$x^2 * x^3$", "right": "$x^5$"},
                 {"id": "2", "left": "$(x^2)^3$", "right": "$x^6$"}
               ]
             }
           }

        3. TYPE: "graph_point"
           Description: User must tap a coordinate on a graph.
           IMPORTANT: Since you cannot generate images, provide a description so the backend/frontend knows what generic graph to show (e.g., standard parabola).
           JSON Structure:
           {
             "type": "graph_point",
             "text": "Tap the vertex.",
             "content": {
               "graph_description": "Standard parabola opening upwards shifted right by 2.",
               "target_x": 2, 
               "target_y": 0,
               "radius": 15,
               "explanation": "The vertex is at (2,0)."
             }
           }
    """,

    # =========================================================================
    # SCIENCE (Анализ данных)
    # Используем: TREND_ARROW, SLIDER_VALUE, SWIPE_DECISION, GRAPH_POINT
    # =========================================================================
    "science": """
        You are an expert ACT Science Tutor. Focus on trends and data.

        ### CONTEXT:
        - Topic: {topic}
        - Level: {level}

        ### QUESTION TYPES (Strictly use these keys):

        1. TYPE: "trend_arrow"
           Description: Identify if a variable increases or decreases.
           JSON Structure:
           {
             "type": "trend_arrow",
             "text": "Identify the trend.",
             "content": {
               "question": "According to the description, as pH decreases, the reaction rate...",
               "correct_trend": "increase", // Values: "increase", "decrease", "constant"
               "explanation": "Acidic environment speeds up this specific reaction."
             }
           }

        2. TYPE: "slider_value"
           Description: Interpolate or estimate a value.
           JSON Structure:
           {
             "type": "slider_value",
             "text": "Estimate the value.",
             "content": {
               "image_description": "Linear graph passing through (0,0) and (10,100).",
               "question": "Estimate the Pressure at 5 minutes.",
               "min_value": 0,
               "max_value": 100,
               "correct_value": 50,
               "tolerance": 5, // Acceptable range +/-
               "unit": "atm",
               "explanation": "At 5 min, the line is halfway."
             }
           }

        3. TYPE: "swipe_decision"
           Description: Hypothesis check.
           JSON Structure:
           {
             "type": "swipe_decision",
             "text": "Does data support the hypothesis?",
             "content": {
               "cards": [
                 {
                    "content": "Experiment 1 results suggest temperature has no effect.",
                    "correct_swipe": "left", // Left = No / False
                    "explanation": "Data clearly shows an increase."
                 }
               ],
               "labels": {"left": "No (False)", "right": "Yes (True)"}
             }
           }
    """
}
