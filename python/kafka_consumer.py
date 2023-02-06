from time import sleep
from json import loads

from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'postgres-sj.public.test',
    bootstrap_servers=['10.10.65.1:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer = lambda x: loads(x.decode('utf-8')))

for message in consumer:
    message = message.value
    print('{}'.format(message))
