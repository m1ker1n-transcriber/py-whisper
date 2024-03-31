import os
import typing


from minio import Minio

from src.util import env


class AudioStorageConfig:
    def __init__(self):
        self.access_key: str = env.must_get('MINIO_ACCESS_KEY')
        self.endpoint: str = env.must_get('MINIO_ENDPOINT')
        self.secret_key: str = env.must_get('MINIO_SECRET_KEY')
        self.secure: bool = env.get_bool('MINIO_SECURE', False)

        # audio_dir is a place where audio files will be placed to be used by transcriber
        # root dir by default
        root_dir = os.path.dirname(os.path.abspath(__file__))
        self.audio_dir: str = os.getenv('AUDIO_DIR', root_dir)

        # well, bucket is not a property of config, but I use the only 1 bucket
        # in the app, so I suppose it's ok to be there
        self.bucket: str = env.must_get('MINIO_BUCKET_NAME')




class AudioStorage:
    def __init__(self, config: AudioStorageConfig = AudioStorageConfig()):
        self.__client = Minio(endpoint=config.endpoint,
                              access_key=config.access_key,
                              secret_key=config.secret_key,
                              secure=config.secure,
                              )
        self.__bucket = config.bucket
        self.__audio_dir = config.audio_dir

    def download_file(self, audio_name: str) -> None:
        """
        Downloads file from minio into provided audio directory.
        """
        self.__client.fget_object(self.__bucket, audio_name, os.path.join(self.__audio_dir, audio_name))


    def delete_file(self, audio_name: str) -> None:
        """
        Deletes file from provided audio directory.
        """
        os.remove(self.path_to_file(audio_name))

    def delete_file_in_bucket(self, audio_name: str) -> None:
        self.__client.remove_object(self.__bucket, audio_name)


    def path_to_file(self, audio_name: str) -> str:
        return os.path.join(self.__audio_dir, audio_name)


    def handle_file(self, audio_name: str, cb: typing.Callable[[str], bool]) -> None:
        """
        Downloads file from minio, handle it by provided callback and remove it from os.
        Also, if handling was successful, removes file from minio as well.
        If not successful, doesn't remove file from minio because it might be handled later?
        :param audio_name: Audio file that has to be handled by cb.
        :param cb: Callback function that takes filepath to audio and returns if handling was successful.
        """
        self.download_file(audio_name)
        success: bool = cb(self.path_to_file(audio_name))
        self.delete_file(audio_name)
        if success:
           self.delete_file_in_bucket(audio_name)
