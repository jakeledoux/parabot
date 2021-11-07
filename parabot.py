import crabber
from dotenv import load_dotenv
from loguru import logger
import os
import random
import sys
from typing import List, Optional

script_dir = os.path.dirname(os.path.realpath(__file__))


def load_quotes(base_dir: Optional[str] = None):
    quote_file = os.path.join(base_dir or '', 'quotes.txt')

    logger.debug('Loading quotes from {}', quote_file)
    if os.path.exists(quote_file):
        # Load quotes from disk
        with open(quote_file, 'r') as f:
            quotes = [quote.strip()
                      for quote in f.read().splitlines()
                      if quote.strip() and not quote.strip().startswith('#')]
        return quotes
    else:
        logger.warning('File does not exist.')


def get_quote(quotes: List[str]):
    logger.debug('Selecting quote from list...')
    quote = random.choice(quotes)
    logger.debug('Chose: "{}"', quote)
    return quote


# Load .env
load_dotenv()

# Setup log
logger.add(os.getenv('LOG_FILE', 'bot.log'))
logger.debug('Program started.')


# Prepare local Crabber connection
if '--test' in sys.argv:
    api_key = os.environ.get('PARABOT_LOCAL_KEY')
    access_token = os.environ.get('PARABOT_LOCAL_TOKEN')
    base_url = 'http://localhost'
# Prepare public Crabber connection
else:
    api_key = os.environ.get('PARABOT_DEPLOY_KEY')
    access_token = os.environ.get('PARABOT_DEPLOY_TOKEN')
    base_url = 'https://crabber.net'

if api_key and access_token:
    logger.debug('Loaded connection settings. URL: {}', base_url)

    # Load quotes from file
    if (quotes := load_quotes(script_dir)):
        # Connect to Crabber instance
        api = crabber.API(api_key, access_token=access_token,
                          base_url=base_url)

        logger.info('Connected to Crabber. (username: @{})',
                    api.get_current_user().username)

        # Send molt
        quote = get_quote(quotes)
        if api.post_molt(quote):
            logger.info('Posted molt successfully.', quote)
        else:
            logger.error('Failed to post molt.')

    else:
        logger.error('No quotes found.')
else:
    logger.error('Environment variables not found.')
