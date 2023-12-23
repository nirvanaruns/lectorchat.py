import time
from TikTokLive import TikTokLiveClient
import pyttsx3
from datetime import datetime
import os
import pygame
import threading

# Inicializar Pygame
pygame.mixer.init()

# Inicializar el motor de texto a voz
engine = pyttsx3.init()

# Variable global para controlar el estado de text-to-speech
tts_enabled = True  # Puedes ajustar el valor inicial según tus necesidades

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
    "_kremling",
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
    "select": "l",
    "_kremling"
}

def ignore_word(word):
    return word.startswith("_") and len(word) > 1 or word.lower() in excluded_words

def get_allowed_user():
    try:
        with open("tiktokchannel.txt", "r") as file:
            return file.read().strip().lower()
    except FileNotFoundError:
        print("El archivo tiktokchannel.txt no se ha encontrado.")
        return None

def get_nick_mapping():
    try:
        with open("nicks.txt", "r") as file:
            lines = file.readlines()
            return {line.split()[0]: line.split()[1].strip() for line in lines}
    except FileNotFoundError:
        print("El archivo nicks.txt no encontrado.")
        return {}

def update_nick_mapping(username, new_nick):
    nick_mapping = get_nick_mapping()
    nick_mapping[username] = new_nick
    with open("nicks.txt", "w") as file:
        for user, nick in nick_mapping.items():
            file.write(f"{user} {nick}\n")

def play_wav(file_name):
    try:
        print(f"Reproduciendo {file_name}")
        pygame.mixer.Sound(file_name).play()
        pygame.time.delay(1000)  # Esperar 1 segundo antes de continuar
    except pygame.error as e:
        print(f"Error al reproducir el archivo {file_name}: {e}")

# Nueva función para renombrar el archivo y activar otro programa
def process_command(file_name, new_name):
    time.sleep(5)  # Esperar 5 segundos antes de revertir el cambio
    os.rename(f"sammicomandos/{file_name}", f"sammicomandos/{new_name}")
    time.sleep(5)  # Esperar 5 segundos
    os.rename(f"sammicomandos/{new_name}", f"sammicomandos/{file_name}")

def on_ttcomment(comment_data):
    global tts_enabled

    username = comment_data.user.nickname
    comment_text = comment_data.comment

    # Verificar si comment_text es None antes de intentar llamar a lower()
    if comment_text is not None:
        comment_text = comment_text.lower()
    else:
        # Manejar el caso en que comment_text sea None
        pass

    username = username.lower()

    allowed_user = get_allowed_user()

    current_time = datetime.now().strftime("%H:%M")
    formatted_comment = f"[{current_time}] {username}: {comment_text}"
    print(formatted_comment)

    words = comment_text.split()
    filtered_words = [word for word in words if not ignore_word(word)]

    # Lista de archivos a procesar
    files_to_process = {
        "_ddleta.txt": "ddleta.txt",
        "_pokemon.txt": "pokemon.txt",
        "_efectoa.txt": "efectoa.txt",
        # Agregar otros archivos según sea necesario
    }

    for src_file, dest_file in files_to_process.items():
        if src_file in words and tts_enabled:
            # 1. Renombrar el archivo a su nuevo nombre
            threading.Thread(target=process_command, args=(src_file, dest_file)).start()

            # 2. Deshabilitar el comando por 5 minutos
            tts_enabled = False
            threading.Timer(300, enable_tts).start()

            # 3. No leer nada si se escriben comandos especiales
            return

    # Verificar si hay comando de cambio de nick
    if "_nick" in words and len(words) > words.index("_nick") + 1:
        new_nick = words[words.index("_nick") + 1]
        update_nick_mapping(username, new_nick)
        username = new_nick  # Actualizar el nombre de usuario para usar el nuevo nick

    # Unir las partes del comentario y leer el resultado en el texto a voz
    final_comment = " ".join(filtered_words)

    nick_mapping = get_nick_mapping()
    if username in nick_mapping:
        username = nick_mapping[username]

    engine.say(f"{username} dijo: {final_comment}")
    engine.runAndWait()

def enable_tts():
    global tts_enabled
    tts_enabled = True

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
