### 1Password CLI helper functions

from awsume.awsumepy.lib.logger import logger
from subprocess import Popen, PIPE
from .config import *
import json


# Cache some 1Password data to avoid multiple calls
PLG_1PASSWORD_ITEM_CACHED = None

def retrieve_item_from_1password(title):
    # TODO: use file cache...
    global PLG_1PASSWORD_ITEM_CACHED
    if PLG_1PASSWORD_ITEM_CACHED is None:
        try:
            process = Popen(['op', 'item', 'get', title, '--format', 'json'],
                    stdout=PIPE, stderr=PIPE)
            output, _ = process.communicate()
            try:
                output_str = output.decode('utf-8') 
                PLG_1PASSWORD_ITEM_CACHED = json.loads(output_str)
            except json.JSONDecodeError:
                logger.error("OP command output is not in JSON format")
                PLG_1PASSWORD_ITEM_CACHED = False
        except FileNotFoundError:
            logger.error('Failed: missing `op` command')
            return None
    return PLG_1PASSWORD_ITEM_CACHED


# Call 1Password to get an OTP for a given vault item.
def get_otp(title):
    try:
        op = Popen(['op', 'item', 'get', '--otp', title],
                   stdout=PIPE, stderr=PIPE)
        linecount = 0
        while True:
            msg = op.stderr.readline().decode()
            if msg == '' and op.poll() is not None:
                break
            elif msg != '' and linecount < MAX_OUTPUT_LINES:
                msg = beautify(msg)
                if msg:
                    safe_print('1Password: ' + msg,
                               colorama.Fore.CYAN)
                    linecount += 1
            else:
                logger.debug(msg.strip('\n'))
        if op.returncode != 0:
            return None
        return op.stdout.readline().decode().strip('\n')
    except FileNotFoundError:
        logger.error('Failed: missing `op` command')
        return None
    

def retrieve_mfa_from_1password_item(config, profile_name):
    title = get_profile_settings_from_1password_config(config, profile_name).get('item')
    if not title:
        logger.debug('No item specified for profile %s' % profile_name)
        return None
    item = retrieve_item_from_1password(title)
    label = "one-time password"
    if item:
        for field in item.get('fields', []):
            if field.get('label', False) == label:
                return field.get('totp')
        logger.debug('No %s found in 1password item %s' % (label, title))

def get_aws_value_in_item(key, item):
    key_conventions = [key, key.replace("_", " "), key.replace("aws_", ""), key.replace("aws_", "").replace("_", " ")]
    for field in item.get('fields', []):
        if field.get('label', False) in key_conventions:
            return field.get('value')
            # safe_print('Obtained %s from 1Password item: %s' % (key, title), colorama.Fore.CYAN)
            # first_profile[key] = field.get('value')
    return None
