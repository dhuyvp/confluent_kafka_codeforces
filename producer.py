#!/usr/bin/env python

# import sys
# from random import choice
# from argparse import ArgumentParser, FileType
# from configparser import ConfigParser
# from confluent_kafka import Producer
import subprocess

# parser = ArgumentParser()
# parser.add_argument('config_file', type=FileType('r'))
# args = parser.parse_args()

# # Parse the configuration.
# # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
# config_parser = ConfigParser()
# config_parser.read_file(args.config_file)
# config = dict(config_parser['default'])

# # Create Producer instance
# producer = Producer(config)

# topic = "codeforces"

def crawl_codeforces():
  subprocess.run(["scrapy", "crawl", "crawl_CF"])


if __name__ == '__main__':
    crawl_codeforces()

    # Block until the messages are sent.
    # producer.poll(10000)
    # producer.flush()