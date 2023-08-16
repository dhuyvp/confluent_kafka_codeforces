#!/usr/bin/env python

import sys
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Consumer, OFFSET_BEGINNING
from discord.ext import commands
import time, datetime
import discord
import os
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()
    MY_BOT_TOKEN_DISCORD = str( os.getenv('MY_BOT_TOKEN_DISCORD') )
    MY_CHANNEL_ID_DISCORD = int( os.getenv('MY_CHANNEL_ID_DISCORD') )

    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument('config_file', type=FileType('r'))
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()

    # Parse the configuration.
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser['default'])
    config.update(config_parser['consumer'])

    # Create Consumer instance
    consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            consumer.assign(partitions)

    # Subscribe to topic
    topic = "codeforces"
    consumer.subscribe([topic], on_assign=reset_offset)

    bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
    # Poll for new messages from Kafka and print them.
    try:
        @bot.event
        async def on_ready():
            print(f'Logged in as {bot.user.name}')
            ###
            channel = bot.get_channel(MY_CHANNEL_ID_DISCORD)
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    # Initial message consumption may take up to
                    # `session.timeout.ms` for the consumer group to
                    # rebalance and start consuming
                    print("Waiting...")
                elif msg.error():
                    print("ERROR: {}".format(msg.error()))
                else:
                    # Extract the (optional) key and value, and print.

                    print("Consumed event from topic {topic} and user_name = {key}: {value}".format(
                        topic=msg.topic(), key=msg.key(), value=msg.value() 
                    ))

                    str_message = msg.value().decode('utf-8')
                    print (str_message)
                    if channel:
                        # Send your message
                        await channel.send(str_message)
                        print('Message sent successfully!')
                    else:
                        print("Channel not found!")
                            
        # Run the bot
        bot.run(MY_BOT_TOKEN_DISCORD)

    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()