import os
import json
import asyncio
from aiokafka import AIOKafkaConsumer
from dotenv import load_dotenv


load_dotenv()

KAFKA_NETWORK = os.getenv("KAFKA_NETWORK", "host.docker.internal:19092")
TOPIC_NAME = os.getenv("TOPIC_NAME", "event-stream-trpl")


async def consume_events() -> None:
	consumer = AIOKafkaConsumer(
		TOPIC_NAME,
		bootstrap_servers=KAFKA_NETWORK,
		group_id="event-consumer-group",
		auto_offset_reset="earliest",
	)

	await consumer.start()
	try:
		print(f"[*] Listening on topic '{TOPIC_NAME}' @ {KAFKA_NETWORK}")
		async for msg in consumer:
			raw = msg.value.decode("utf-8")
			try:
				data = json.loads(raw)
			except json.JSONDecodeError:
				print(f"[WARN] Non-JSON message: {raw}")
				continue

			event_type = data.get("type", "UNKNOWN")
			sender = data.get("sender")
			receiver = data.get("receiver")
			amount = data.get("amount")

			print(f"[EVENT] type={event_type} sender={sender} receiver={receiver} amount={amount}")
	finally:
		await consumer.stop()


if __name__ == "__main__":
	asyncio.run(consume_events())
