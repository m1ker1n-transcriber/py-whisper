import whisper


class Transcriber:
    def __init__(self, model_name: str = "small", verbose: bool = True):
        self.__model_name: str = model_name
        self.verbose: bool = verbose
        self.__model = whisper.load_model(model_name)

    def transcribe(self, audio_name: str, verbose: bool | None = None) -> str:
        if verbose is None:
            verbose = self.verbose
        result = self.__model.transcribe(audio_name, verbose=verbose)
        return result['text']

