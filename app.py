import queue, time, threading, signal, sys, os, base64
from continous_vad_monitor import record_with_vad
from tts import talk
from stt import convert_speech_to_text
from analyze_user_input import analyze_text
from PIL import ImageGrab
from llm import llm_response
from datetime import datetime

if __name__ == "__main__":

    def handle_sigint(sig, frame):
        print('sigint was clicked!')
        sys.exit(0)
    signal.signal(signal.SIGINT, handle_sigint)

    wav_files_queue = queue.Queue()
    stop_event = threading.Event()

    # record the user
    t = threading.Thread(target=record_with_vad, args=(wav_files_queue, stop_event), daemon=True)
    t.start()

    while True:
        time.sleep(1)
        wav_file = wav_files_queue.get()
        if wav_file:
            
            # Print only the time
            print('transcribing: ', datetime.now().strftime("%H:%M:%S"))
            transcription = convert_speech_to_text(wav_file)
            print(transcription)
            os.remove(wav_file)
        
            
            print('send to llm text + screenshot: ', datetime.now().strftime("%H:%M:%S"))
            llm_res = llm_response(transcription)
            print(llm_res)

            print('start talking: ', datetime.now().strftime("%H:%M:%S"))
            stop_event.set()
            talk(llm_res)

            print('after talk in app')
            stop_event.clear()
            t = threading.Thread(target=record_with_vad, args=(wav_files_queue, stop_event), daemon=True)
            t.start()
    