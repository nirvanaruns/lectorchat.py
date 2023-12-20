import time  # Importar el módulo time para gestionar el tiempo
from TikTokLive import TikTokLiveClient  # Importar la clase TikTokLiveClient del módulo TikTokLive
import pyttsx3  # Importar el módulo pyttsx3 para texto a voz
from datetime import datetime  # Importar la clase datetime del módulo datetime
import os  # Importar el módulo os para operaciones del sistema
import pygame  # Importar el módulo pygame para reproducción de sonido
import threading  # Importar el módulo threading para manejar subprocesos
import pyautogui  # Importar el módulo pyautogui para control de teclado

# Inicializar Pygame
pygame.mixer.init()

# Inicializar el motor de texto a voz
engine = pyttsx3.init()

# Variable global para controlar el estado de text-to-speech
tts_enabled = True

# Variable global para controlar el tiempo de espera entre ejecuciones del comando "_a"
last_a_command_time = {}

# Lista de palabras a ignorar en el text-to-speech
excluded_words = {
    "arriba": "w",
    "abajo": "s",
    "izquierda": "a",
    "derecha": "d",
    "botona": "q",
    "botonb": "e",
    "botonl": "o",
    "botonr": "p",
    "carriba": "y",
    "cabajo": "h",
    "cizquierda": "g",
    "cderecha": "j",
    "start": "m",
    "select": "l",
    # Inglés
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",
    "buttona": "q",
    "buttonb": "e",
    "buttonl": "o",
    "buttonr": "p",
    "cup": "y",
    "cdown": "h",
    "cleft": "g",
    "cright": "j",
    "start": "m",
    "select": "l"
}

# Función para determinar si una palabra debe ser ignorada
def ignore_word(word):
    return word.startswith("_") and len(word) > 1 or word.lower() in excluded_words

# Obtener el usuario permitido desde el archivo tiktokchannel.txt
def get_allowed_user():
    try:
        with open("tiktokchannel.txt", "r") as file:
            return file.read().strip().lower()
    except FileNotFoundError:
        print("El archivo tiktokchannel.txt no se ha encontrado.")
        return None

# Obtener el mapeo de apodos desde el archivo nicks.txt
def get_nick_mapping():
    try:
        with open("nicks.txt", "r") as file:
            lines = file.readlines()
            return {line.split()[0]: line.split()[1].strip() for line in lines}
    except FileNotFoundError:
        print("El archivo nicks.txt no encontrado.")
        return {}

# Actualizar el mapeo de apodos en el archivo nicks.txt
def update_nick_mapping(username, new_nick):
    nick_mapping = get_nick_mapping()
    nick_mapping[username] = new_nick
    with open("nicks.txt", "w") as file:
        for user, nick in nick_mapping.items():
            file.write(f"{user} {nick}\n")

# Reproducir un archivo WAV usando Pygame
def play_wav(file_name):
    try:
        print(f"Reproduciendo {file_name}")
        pygame.mixer.Sound(file_name).play()
        pygame.time.delay(1000)  # Esperar 1 segundo antes de continuar
    except pygame.error as e:
        print(f"Error al reproducir el archivo {file_name}: {e}")

# Función para manejar eventos de comentarios de TikTok
def on_ttcomment(comment_data):
    global tts_enabled, last_a_command_time

    username = comment_data.user.nickname
    comment_text = comment_data.comment

    if comment_text is not None:
        comment_text = comment_text.lower()

    username = username.lower()

    allowed_user = get_allowed_user()

    current_time = datetime.now().strftime("%H:%M")
    formatted_comment = f"[{current_time}] {username}: {comment_text}"
    print(formatted_comment)

    words = comment_text.split()
    filtered_words = [word for word in words if not ignore_word(word)]

    if tts_enabled:
        final_output = []

        for word in words:
            if ignore_word(word):
                wav_file = f"Audios/{word}.wav"
                if os.path.exists(wav_file):
                    play_wav(wav_file)
            else:
                final_output.append(word)

        if "_nick" in words and len(words) > words.index("_nick") + 1:
            new_nick = words[words.index("_nick") + 1]
            update_nick_mapping(username, new_nick)
            username = new_nick

        final_comment = " ".join(final_output)

        nick_mapping = get_nick_mapping()
        if username in nick_mapping:
            username = nick_mapping[username]

        engine.say(f"{username} dijo: {final_comment}")
        engine.runAndWait()

    # Verificar si se recibió el comando "_a"
    if "_a" in words:
        current_time = time.time()

        # Verificar si ha pasado al menos 10 minutos desde la última ejecución de "_a" por cualquier usuario
        if current_time - last_a_command_time.get(username, 0) > 600:
            # Puede ejecutar el comando "_a"
            last_a_command_time[username] = current_time
        else:
            print("Espera al menos 10 minutos entre ejecuciones del comando '_a'.")

    # Verificar si se recibió el comando "_kremling" o cualquier otro comando en el directorio /Audios/
    if words and words[0].startswith("_") and os.path.exists(f"Audios/{words[0]}.wav"):
        play_wav(f"Audios/{words[0]}.wav")

# Punto de entrada principal
if __name__ == "__main__":
    allowed_user = get_allowed_user()

    if allowed_user:
        tiktok_username = "@" + allowed_user
        tiktok_client = TikTokLiveClient(unique_id=tiktok_username)

        on_ttcomment_event = tiktok_client.on("comment")(on_ttcomment)

        print("Connected")
        tiktok_client.run()

        while True:
            time.sleep(1)
    else:
        print("No se ha especificado un nombre de usuario en tiktokchannel.txt.")
