import sys, wave, signal, queue, time
import numpy as np
import sounddevice as sd
import webrtcvad
from scipy.signal import resample_poly
import whisper
# ---------- Your existing configuration ----------
DEVICE_INDEX = 25       # keep the device you verified works
CHANNELS = 1
DTYPE = "float32"
OUTPUT = "capture.wav"
TARGET_SR = 16000
TALKING_THRESHOLD = 15
SILENCE_THRESHOLD = 40
# ---------- VAD / framing configuration ----------
FRAME_MS = 20                 # VAD supports 10/20/30 ms frames
VAD_AGGRESSIVENESS = 2        # 0..3 (3 = most sensitive)
ENTER_FRAMES = 3              # need ~60 ms of speech to enter "talking"
EXIT_FRAMES = 25              # need ~500 ms of silence to exit "talking"

def record_with_vad(wav_files_queue, stop_event):
    while not stop_event.is_set():
        dev = sd.query_devices(None, 'input')
        CAPTURE_SR = int(dev['default_samplerate'])
        IN_BLOCK = int(round(CAPTURE_SR * 0.02))
        buffer = bytearray() 
        print(f"Recording...")

        # Queued blocks from the callback (float32 [-1,1], shape = (n_frames, 1))
        q = queue.Queue()

        # Open WAV only after stream actually opens
        wf = None
        file_index = 0
        # --- VAD state ---
        vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

        in_talking = False
        speech_count = 0
        silence_count = 0

        def audio_callback(indata, frames, time_info, status):
            q.put(indata.copy())

        try:
            with sd.InputStream(channels=CHANNELS,
                                dtype=DTYPE,
                                blocksize=IN_BLOCK,
                                callback=audio_callback):
                while True:
                    block = q.get()  # np.float32, shape (IN_BLOCK, 1)
                    block_16k = resample_poly(block, TARGET_SR, CAPTURE_SR).astype(np.float32)

                    # --- Write to file as int16 ---
                    pcm16_block = (np.clip(block_16k[:, 0], -1.0, 1.0) * 32767).astype(np.int16)
                    block_bytes = pcm16_block.tobytes()
                    is_speech = vad.is_speech(block_bytes, TARGET_SR)

                    if is_speech:
                        silence_count = 0
                        speech_count += 1
                        buffer += block_bytes

                        if not in_talking and speech_count > TALKING_THRESHOLD:
                            in_talking = True    
                            print(">>> START TALKING")
                    else:
                        silence_count += 1
                        speech_count = 0
                        if in_talking:
                            buffer += block_bytes
                            if in_talking and silence_count > SILENCE_THRESHOLD:
                                in_talking = False
                                print("<<< STOP TALKING")
                                curr_filename = f"{file_index}{OUTPUT}"
                                wf = wave.open(curr_filename , "wb")
                                wf.setnchannels(CHANNELS)
                                wf.setsampwidth(2)       # int16
                                wf.setframerate(TARGET_SR)
                                wf.writeframes(buffer)
                                wf.close()
                                wav_files_queue.put(curr_filename)
                                file_index += 1
                        else:
                            buffer = bytearray()
                            
        except KeyboardInterrupt:
            print("\nStopping…")

if __name__ == "__main__":
    wav_files_queue = queue.Queue()
    record_with_vad(wav_files_queue)
