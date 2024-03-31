import os
import sys

from src.audio_storage import AudioStorage
from src.dto.result import ResultDTO
from src.dto.task import TaskDTO
from src.queue import Queue
from src.transcriber import Transcriber


def main():
    audio_storage = AudioStorage()
    transcriber = Transcriber()
    queue = Queue()

    def queue_callback(task: TaskDTO) -> (ResultDTO, bool):
        result: ResultDTO = ResultDTO(task.telegram_user_id, task.telegram_msg_id, '')

        def audio_storage_callback(audio_name) -> bool:
            transcription: str = transcriber.transcribe(audio_name=audio_name)
            result.transcription = transcription
            return True
        audio_storage.handle_file(task.voice_id, audio_storage_callback)

        return result, True

    queue.start_handling(queue_callback)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
