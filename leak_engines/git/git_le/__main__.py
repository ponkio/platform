__version__ = '0.0.1'
from distutils.command.config import config
import click
import sys
import logging
import yaml 

from git_le.Commands import *

logger = logging.getLogger("git_le")

class Config(object):
    def _check_config(self, config_file):
        try:
            with open(config_file, 'r') as f:
                f.close()
        except Exception as err:
            logger.error(f'Unable to open configuraiton file: {err}')
            return False
        return True

    def __init__(self, config_file=None):
        if self._check_config(config_file):
            try:
                with open(config_file, 'r') as c:
                    parsed_config = yaml.safe_load(c)
                    self.config = parsed_config
            except yaml.YAMLError as err:
                logger.error(f'Unable to parse configuration file: {err}')
        else:
            self.config = config_file

@click.group()
@click.option('--config', help='Path to configuration file.', envvar='GIT_LE_CONFIG', required=False)
@click.pass_context
def cli(ctx, config):
    pass
    #ctx.obj = Config(config)
        

@cli.command()
@click.option('--type', help='Type of consumer to start running.',type=click.Choice(['mq'], case_sensitive=False), required=True)
@click.option('--aqmp-url', help='RabbitMQ aqmp url.', envvar='GIT_LE_AQMP_URL', required=False)
@click.pass_obj
def producer(config, **kwargs):
    """ Generate feed of public git repos 
    
    """
    Producer.run(config, kwargs)

@cli.command()
@click.option('--type', help='Type of consumer to start running.',type=click.Choice(['mq', 'lambda'], case_sensitive=False), required=True)
@click.option('--aqmp-url', help='RabbitMQ aqmp url.', envvar='GIT_LE_AQMP_URL', required=False)
@click.option('--mongo-url', help='MongoDB url. ', envvar='GIT_LE_MONGO_URL', required=False)
@click.pass_obj
def consumer(config, **kwargs):
    """ Consume a feed of public repos and execute secret detection on each.
    
    """
    #print(config)
    config = None
    try:
        Consumer.run(config, kwargs)
    except Exception as err:
        click.echo(f"[!] {err}")
        sys.exit(1)

def main():
    if not logger.handlers:
        st_handler = logging.StreamHandler()

        #st_handler.setFormatter(logging.Formatter('%(asctime)s [%levelname)-4s][%(module)s.%(funcName)s%(arg)s]: %(message)s'))
        #logger.addHandler(st_handler)
        logger.setLevel(logging.INFO)
        
    cli()