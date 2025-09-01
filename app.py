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
            print('convert to text: ', datetime.now().strftime("%H:%M:%S"))

            # get transcription
            transcription = convert_speech_to_text(wav_file)
            print(transcription)

            print('remove wav file: ', datetime.now().strftime("%H:%M:%S"))
            os.remove(wav_file)

            print('analyze if transcription is a question: ', datetime.now().strftime("%H:%M:%S"))
            # analyze transcription
            res = analyze_text(transcription)

            print(res)
            if res.is_question_for_llm:
                if res.is_screenshot_required:
                    print('take a screenshot: ', datetime.now().strftime("%H:%M:%S"))
                    ImageGrab.grab(all_screens=True).save('screenshot.png')

                    print('encode the file to base64: ', datetime.now().strftime("%H:%M:%S"))
                    with open('screenshot.png', "rb") as f:
                        img_base64 = base64.b64encode(f.read()).decode("utf-8")
                    
                    print('send to llm text + screenshot: ', datetime.now().strftime("%H:%M:%S"))
                    llm_res = llm_response(transcription, img_base64)
                    print(llm_res)

                    print('start talking: ', datetime.now().strftime("%H:%M:%S"))
                    stop_event.set()
                    talk(llm_res)
                    print('after talk in app')
                    stop_event.clear()
                    t = threading.Thread(target=record_with_vad, args=(wav_files_queue, stop_event), daemon=True)
                    t.start()
                else:
                    print('this is a question of the llm!')

            else:
                print('this doesnt require a response......')
    