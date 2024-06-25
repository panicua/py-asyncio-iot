import asyncio
import time
from typing import Any, Awaitable

from iot.devices import HueLightDevice, SmartSpeakerDevice, SmartToiletDevice
from iot.message import Message, MessageType
from iot.service import IOTService


async def parallel_handling(*services: Awaitable[Any]) -> tuple:
    return await asyncio.gather(*services)


async def sequence_handling(*services: Awaitable[Any]) -> None:
    for service in services:
        await service


async def main() -> None:
    # create an IOT service
    service = IOTService()

    # create devices
    hue_light = HueLightDevice()
    speaker = SmartSpeakerDevice()
    toilet = SmartToiletDevice()

    # register devices in parallel
    hue_light_id, speaker_id, toilet_id = await parallel_handling(
        service.register_device(hue_light),
        service.register_device(speaker),
        service.register_device(toilet),
    )

    # Wake-up program
    await parallel_handling(
        service.send_msg(Message(hue_light_id, MessageType.SWITCH_ON)),
        sequence_handling(
            service.send_msg(Message(speaker_id, MessageType.SWITCH_ON)),
            service.send_msg(Message(
                speaker_id,
                MessageType.PLAY_SONG,
                "Rick Astley - Never Gonna Give You Up"
            ))
        )
    )

    # Sleep program
    await parallel_handling(
        service.send_msg(Message(hue_light_id, MessageType.SWITCH_OFF)),
        service.send_msg(Message(speaker_id, MessageType.SWITCH_OFF)),
        sequence_handling(
            service.send_msg(Message(toilet_id, MessageType.FLUSH)),
            service.send_msg(Message(toilet_id, MessageType.CLEAN))
        )
    )

    unregister_tasks = [
        service.unregister_device(hue_light_id),
        service.unregister_device(speaker_id),
        service.unregister_device(toilet_id),
    ]
    await asyncio.gather(*unregister_tasks)


if __name__ == "__main__":
    start = time.perf_counter()
    asyncio.run(main())
    end = time.perf_counter()

    print("Total elapsed:", end - start)
