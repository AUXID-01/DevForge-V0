import time

class LatencyLogger:
    @staticmethod
    def compute_latency(end_of_speech_time: float) -> float:
        """
        end_of_speech_time is provided by ASR.
        Return computed wall time latency in milliseconds.
        """
        now = time.time() * 1000  # ms
        return now - end_of_speech_time

    @staticmethod
    def log(label: str, latency_ms: float):
        print(f"[LATENCY] {label}: {latency_ms:.2f} ms")
