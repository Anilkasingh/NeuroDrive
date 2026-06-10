class Sample:
    def __init__(self, eeg1: float, eeg2: float, ecg: float, time: str, recording_id: int):
        self.eeg1 = eeg1
        self.eeg2 = eeg2
        self.ecg = ecg
        self.time = time
        self.recording_id = recording_id

class Recording:
    def __init__(self, id: int, time_from: str, time_to: str, user_id: int, samples: list[Sample], user):
        self.id = id
        self.time_from = time_from
        self.time_to = time_to
        self.user_id = user_id
        self.samples = samples
        self.user = user
