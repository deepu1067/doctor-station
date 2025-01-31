import threading
import wave
import pyaudio


class AudioRecorder:
    def __init__(self, chunk=1024, frmat=pyaudio.paInt16, channels=2, rate=44100):
        self.CHUNK = chunk
        self.FORMAT = frmat
        self.CHANNELS = channels
        self.RATE = rate
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.st = 0  # Flag to control recording
        self.thread = None
        self.stream = None

    def start_record(self):
        if self.st == 1:
            print("Recording is already in progress.")
            return
        self.st = 1
        self.frames = []
        print("Starting recording...")
        self.thread = threading.Thread(target=self.record)
        self.thread.start()

    def record(self):
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        try:
            while self.st == 1:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                self.frames.append(data)
        except Exception as e:
            print(f"Error while recording: {e}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            print("Recording loop stopped.")

    def stop_record(self, output_filename='output.wav'):
        if self.st == 0:
            print("No recording is in progress.")
            return
        self.st = 0  # Stops the recording loop
        if self.thread:
            self.thread.join()
        print(f"Saving recording to {output_filename}...")
        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        print("File saved successfully.")

    def close(self):
        if self.p:
            self.p.terminate()
