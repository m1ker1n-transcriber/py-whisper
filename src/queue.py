import typing

import pika
import json

from src.dto.result import ResultDTO
from src.dto.task import TaskDTO
from src.util import env


class QueueConfig:
    def __init__(self):
        self.url: str = env.must_get('AMQP_URL')
        self.task_queue: str = env.must_get('AMQP_TASK_QUEUE_NAME')
        self.result_queue: str = env.must_get('AMQP_RESULTS_QUEUE_NAME')


class Queue:
    def __init__(self, config: QueueConfig = QueueConfig()):
        self.__connection = pika.BlockingConnection(pika.URLParameters(config.url))
        self.__channel = self.__connection.channel()

        self.__task_queue = config.task_queue
        self.__channel.queue_declare(queue=config.task_queue)
        self.__result_queue = config.result_queue
        self.__channel.queue_declare(queue=config.result_queue)

    def start_handling(self, cb: typing.Callable[[TaskDTO], typing.Tuple[ResultDTO, bool]]) -> None:
        """
        :param cb: callback function which handling dto.task.TaskDTO returning:
            - result: dto.result.ResultDTO
            - success: bool - if task was successful handled
        """

        def on_message(ch, method: pika.spec.Basic.Deliver, properties, body: bytes) -> None:
            # Receiving and unpacking message from task queue
            print(f" [v] Received {body}")
            data = json.loads(body)
            try:
                telegram_user_id = data['telegram_user_id']
                telegram_msg_id = data['telegram_msg_id']
                voice_id = data['voice_unique_id']
            except KeyError as err:
                print(f" [x] Unknown key {err}")
                return
            task = TaskDTO(telegram_user_id, telegram_msg_id, voice_id)

            # Handling task by provided callback
            result, success = cb(task)

            if not success:
                print(f" [x] Result was bad")
                return

            # Pushing result into result queue
            self.__channel.basic_publish(exchange='',
                                         routing_key=self.__result_queue,
                                         body=json.dumps(
                                             vars(result),
                                             ensure_ascii=False
                                            )
                                         )
            print(f" [v] Sent result to result queue")

            # Sending acknowledge to task queue
            self.__channel.basic_ack(delivery_tag=method.delivery_tag)
            print(f" [v] Sent ack to task queue")

        self.__channel.basic_consume(queue=self.__task_queue, on_message_callback=on_message, auto_ack=False)
        print(f" [v] Start consuming tasks")
        self.__channel.start_consuming()
