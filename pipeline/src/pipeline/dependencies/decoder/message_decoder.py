import logging
import typing

import orjson
from confluent_kafka import Message

from pipeline.dependencies.decoder.message_map import (MessageTypeMap,
                                                       get_message_type_map)


class MessageDecoder:
    message_map: MessageTypeMap
    use_kafka: bool
    logger: logging.Logger

    def __init__(self, use_kafka: bool, logger: logging.Logger):
        self.message_map = get_message_type_map()
        self.use_kafka = use_kafka
        self.logger = logger

    async def get_payload_model(
        self, message: Message | dict, use_kafka: bool
    ) -> tuple[typing.Any]:
        if use_kafka:
            assert isinstance(message, Message)
            message_content = message.value()
        else:
            message_content = message
        model = self.message_map.get_model_by_message_type(
            message_content["message_type"]
        )
        if not model:
            raise ValueError(f"Unknown message type in message : {message_content}")
        try:
            validated_model = model(**message_content)
        except Exception as e:
            print(f"Failed to validate model: {e}")
            raise
        return validated_model.get_tuple_for_insertion()

    async def decode_payload(
        self,
        message: Message | dict,
        use_kafka: bool,
    ) -> tuple:
        """Decodes the contents of the payload into a viable application model."""
        if use_kafka:
            message = await self.decode_wire_message(message)
        wire_model = await self.get_payload_model(message=message, use_kafka=use_kafka)
        return wire_model

    async def decode_messages(
        self, messages: list[Message | dict], use_kafka: bool = True
    ) -> typing.AsyncGenerator[tuple, None]:
        for message in messages:
            decoded = await self.decode_payload(message, use_kafka=use_kafka)
            if decoded is not None:
                yield decoded

    async def decode_wire_message(self, message: Message | dict) -> Message:
        if self.use_kafka:
            assert isinstance(message, Message)
            payload = message.value()
            assert isinstance(payload, bytes)
            try:
                payload_dict = orjson.loads(payload)
            except:
                msg = ("failed to decode payload %s", payload)
                raise ValueError(msg)
            message.set_value(payload_dict)
        return message
