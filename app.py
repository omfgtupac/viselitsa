import random
import streamlit as st
from PIL import Image

@st.cache_data
def choose_word(used_words):
    with open("words.txt", mode="r", encoding='utf-8') as words:
        wordlist = [line.strip().lower() for line in words if line.strip()]
    available_words = [word for word in wordlist if word not in used_words]

    if not available_words:
        return None
    word = random.choice(available_words)
    used_words.append(word)
    return word

def display_hangman_image(tries):
    image_path = f"images/hangman_{tries}.png"
    return Image.open(image_path)

def reset_game():
    new_word = choose_word(st.session_state.used_words)
    st.session_state.word = new_word
    st.session_state.word_completion = "_" * len(st.session_state.word)
    st.session_state.guessed_letters = []
    st.session_state.tries = 7
    st.session_state.guessed = False


def game():
    engl = 'abcdefghijklmnopqrstuvwxyz'
    if "used_words" not in st.session_state:
        st.session_state.used_words = []

    st.set_page_config(layout="wide")
    st.header("Добро пожаловать в Виселицу!")

    if "word" not in st.session_state:
        reset_game()

    word = st.session_state.word
    word_completion = st.session_state.word_completion
    guessed_letters = st.session_state.guessed_letters
    tries = st.session_state.tries
    guessed = st.session_state.guessed

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(display_hangman_image(tries), width=500)
    with (col2):
        st.write(f"Слово содержит {len(word)} букв.")
        word_text = st.text("Слово: " + word_completion)

        guess = st.text_input("Введите букву: ").lower()
        if guessed or tries == 0:
            if guessed:
                st.success(f"Поздравляем! Вы угадали слово: {word}")
                st.session_state.used_words.append(word)
            else:
                st.error(f"Вы проиграли. Загаданное слово было: {word}")
                st.session_state.used_words.append(word)

            if st.button("Начать заново"):
                reset_game()
            return

        if st.button("Проверить"):
            if len(guess) == 1 and guess.isalpha():
                if guess in guessed_letters:
                    st.warning(f"Вы уже угадывали эту букву: {guess}")
                elif guess not in word:
                    if guess in engl:
                        st.warning('Поменяйте раскладку клаиватуры. Вам необходимо ввести русскую букву')
                    else:
                        st.error(f"В слове нет буквы: {guess}")
                        st.session_state.tries -= 1
                        guessed_letters.append(guess)
                else:
                    st.success(f"Вы угадали букву: {guess}")
                    guessed_letters.append(guess)
                    word_completion = list(word_completion)
                    locations = [i for i, letter in enumerate(word) if letter == guess]
                    for location in locations:
                        word_completion[location] = guess
                    word_completion = "".join(word_completion)
                    st.session_state.word_completion = word_completion
                    word_text.text("Слово: " + word_completion)

                    if "_" not in st.session_state.word_completion:
                        st.session_state.guessed = True

            else:
                st.error("Недопустимый ввод.")

if __name__ == "__main__":
    game()