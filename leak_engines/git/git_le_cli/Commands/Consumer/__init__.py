import click
import logging

from git_le_cli.Commands.Consumer.consumer_wrapper import Consumer_wrapper


logger = logging.getLogger("git_le_cli")

def _run_mq(mq_config):
    aqmp_url = mq_config.get('aqmp_url')
    mongo_url = mq_config.get('mongo_url')
    consumer = Consumer_wrapper(aqmp_url, mongo_url)
    click.echo("[+] Runing mq consumer")

    consumer.run()


def _run_lambda(lambda_config): 
    click.echo("[+] Runing lambda consumer")
    pass

def run(config, kwargs):

    print(kwargs)

    mq_config = {
        "aqmp_url":kwargs.get('aqmp_url'),
        "mongo_url":kwargs.get('mongo_url')
    }

    consumer_type = kwargs.get('type')
    if consumer_type.lower() == 'mq':
        _run_mq(mq_config)
    elif consumer_type.lower() == 'lambda':
        _run_lambda(lambda_config)
