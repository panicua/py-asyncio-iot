import asyncio
import time
from typing import Any, Awaitable

from iot.devices import HueLightDevice, SmartSpeakerDevice, SmartToiletDevice
from iot.message import Message, MessageType
from iot.service import IOTService


async def main() -> None:
    # create an IOT service
    service = IOTService()

    # create devices
    hue_light = HueLightDevice()
    speaker = SmartSpeakerDevice()
    toilet = SmartToiletDevice()

    # register devices in parallel
    start_ = time.perf_counter()
    hue_light_id, speaker_id, toilet_id = await parallel_handling(
        service.register_device(hue_light),
        service.register_device(speaker),
        service.register_device(toilet)
    )
    end_ = time.perf_counter()
    print("Elapsed for device registration:", end_ - start_)

    # create a few programs
    wake_up_program = [
        Message(hue_light_id, MessageType.SWITCH_ON),
        Message(speaker_id, MessageType.SWITCH_ON),
        Message(speaker_id, MessageType.PLAY_SONG,
                "Rick Astley - Never Gonna Give You Up"),
    ]

    sleep_program = [
        Message(hue_light_id, MessageType.SWITCH_OFF),
        Message(speaker_id, MessageType.SWITCH_OFF),
        Message(toilet_id, MessageType.FLUSH),
        Message(toilet_id, MessageType.CLEAN),
    ]

    # run the programs
    await service.run_program(wake_up_program)
    await service.run_program(sleep_program)


async def parallel_handling(*services: Awaitable[Any]) -> list:
    return await asyncio.gather(*services)


if __name__ == "__main__":
    start = time.perf_counter()
    asyncio.run(main())
    end = time.perf_counter()

    print("Total elapsed:", end - start)
