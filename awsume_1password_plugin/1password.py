import argparse
import colorama
import traceback
import sys

from awsume.awsumepy import hookimpl, safe_print
from awsume.awsumepy.lib import profile as profile_lib
from awsume.awsumepy.lib import cache as cache_lib
from awsume.awsumepy.lib.logger import logger

from .helpers.profile import *
from .helpers.opCLI import *
from .helpers.config import *


# Truncate proxied subprocess output to avoid stack trace spam
MAX_OUTPUT_LINES = 2

# Map an MFA serial to a 1Password vault item
def find_item(config, mfa_serial):
    config = config.get('1password')
    item = None
    if not config:
        logger.debug('No config subsection')
    elif type(config) == str:
        item = config
    elif type(config) == dict:
        item = config.get(mfa_serial)
    else:
        logger.debug('Malformed config subsection')
        return
    if not item:
        logger.debug('No vault item specified for this mfa_serial')
    return item


# Find the MFA serial for a given AWS profile.
def get_mfa_serial(profiles, target_name):
    mfa_serial = profile_lib.get_mfa_serial(
        profiles, target_name)
    if not mfa_serial:
        logger.debug('No MFA required')
    return mfa_serial


# Make a 1Password error message more succinct before safe_printing it.
# Return None if it's not worth printing (e.g. an expected error).
def beautify(msg):
    if msg.startswith('[ERROR]'):
        return msg[28:]  # len('[ERROR] 2023/02/04 16:29:52')
    elif msg.startswith('error initializing client:'):
        return msg[26:]  # len('error initializing client:')
    else:
        return msg


### START Manage awsume profiles adding aws keys directly from 1password CLI, withous pass via ~/.aws/credentials ###
# Hydrate a profile with credentials from 1password, if not specified in the profile itself
def hydrate_profile(config, first_profile_name, first_profile):
    cfg = get_profile_settings_from_1password_config(config, first_profile_name)
    if not cfg:
        logger.debug('No 1password config for profile %s, skip aws_credentials check' % first_profile_name)
        return None
    if not cfg.get('item'):
        logger.debug('No 1password item title spefified for profile %s, skip aws_credentials check' % first_profile_name)
        return None
    hydrate_key_from_1password('aws_access_key_id', first_profile, first_profile_name, cfg.get('item'))
    hydrate_key_from_1password('aws_secret_access_key', first_profile, first_profile_name, cfg.get('item'))

def hydrate_key_from_1password(key, first_profile, first_profile_name, title):
    if not first_profile.get(key):
        logger.debug('No %s setted for %s, try to retrieve from 1password' % (key, first_profile_name))
        item = retrieve_item_from_1password(title)
        if item:
            value = get_aws_value_in_item(key, item)
            if(value):
                safe_print('Obtained %s from 1Password item: %s' % (key, title), colorama.Fore.CYAN)
                first_profile[key] = value
            else:
                logger.error('No %s found in 1password item %s' % (key, title))
### END Manage awsume profiles adding aws keys directly from 1password CLI, withous pass via ~/.aws/credentials ###


# Print sad message to console with instructions for filing a bug report.
# Log stack trace to stderr in lieu of safe_print.
def handle_crash():
    safe_print('Error invoking 1Password plugin; please file a bug report:\n  %s' %
               ('https://github.com/xeger/awsume-1password-plugin/issues/new/choose'), colorama.Fore.RED)
    traceback.print_exc(file=sys.stderr)


@hookimpl
def pre_get_credentials(config: dict, arguments: argparse.Namespace, profiles: dict):
    try:
        target_profile_name = profile_lib.get_profile_name(config, profiles, arguments.target_profile_name)
        target_profile = profiles.get(target_profile_name)

        # If thre's no profile then skip because it's yet managed from awsume
        if not target_profile:
            logger.debug('No profile %s found, skip plugin flow' % target_profile_name)
            return None

        if target_profile_name != None:

            # Create fake profile to be compliant with op plugin, that permits to avoid source_profile in ~/.aws/config
            if not has_some_source(target_profile):
                set_fake_profile(profiles, target_profile_name)
            # If the source profile is not setted into ~/.aws/credentials but is associated to a 1password item censed into configs, create it
            elif not is_source_profile_registered(profiles, target_profile) and is_profile_registered_in_1password_config(config, target_profile):
                profiles[target_profile.get('source_profile')] = {}

            role_chain = profile_lib.get_role_chain(config, arguments, profiles, target_profile_name)
            first_profile_name = role_chain[0]
            first_profile = profiles.get(first_profile_name)
            hydrate_profile(config, first_profile_name, first_profile)
            source_credentials = profile_lib.profile_to_credentials(first_profile)

            cache_file_name = 'aws-credentials-' + source_credentials.get('AccessKeyId')
            cache_session = cache_lib.read_aws_cache(cache_file_name)
            valid_cache_session = cache_session and cache_lib.valid_cache_session(cache_session)

            mfa_serial = profile_lib.get_mfa_serial(profiles, first_profile_name)
            if mfa_serial and (not valid_cache_session or arguments.force_refresh) and not arguments.mfa_token:
                mfa_token = None
                # maintain old behaviour via direct mfa_serial <-> 1password_title mapping if setted in config
                item = find_item(config, mfa_serial)
                if item:
                    mfa_token = get_otp(item)
                else:
                    mfa_token = retrieve_mfa_from_1password_item(config, first_profile_name)
                if mfa_token:
                    arguments.mfa_token = mfa_token
                    safe_print('Obtained MFA token from 1Password item.', colorama.Fore.CYAN)

    except Exception:
        handle_crash()
