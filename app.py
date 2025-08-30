import queue, time, threading, signal, sys
from continous_vad_monitor import record_with_vad
from stt import convert_speech_to_text
from analyze_user_input import analyze_text

if __name__ == "__main__":

    def handle_sigint(sig, frame):
        print('sigint was clicked!')
        sys.exit(0)
    signal.signal(signal.SIGINT, handle_sigint)

    wav_files_queue = queue.Queue()

    # record the user
    t = threading.Thread(target=record_with_vad, args=(wav_files_queue,), daemon=True)
    t.start()

    while True:
        time.sleep(1)
        wav_file = wav_files_queue.get()
        if wav_file:
            text = convert_speech_to_text(wav_file)
            print(text)
            res = analyze_text(text)
            print(res)