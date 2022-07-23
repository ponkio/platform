import click
from git_le_cli.Commands.Consumer.consumer_wrapper import Consumer_wrapper

def _run_mq(mq_config):
    aqmp_url = mq_config.get('aqmp_url')
    consumer = Consumer_wrapper(aqmp_url)
    click.echo("[+] Runing mq consumer")

    consumer.run()


def _run_lambda(lambda_config): 
    click.echo("[+] Runing lambda consumer")
    pass

def run(config, kwargs):

    if len([x for x in config.get('consumer').keys()]) > 1:
        raise Exception('Too many connection options configured')

    consumer_config = config.get('consumer')
    mq_config = consumer_config.get('mq')
    lambda_config = consumer_config.get('sqs')

    if mq_config:
        _run_mq(mq_config)
    elif lambda_config:
        _run_lambda(lambda_config)
