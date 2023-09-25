#### START Manage AWS profiles and aws files ~/.aws/config ~/.aws/credentials compatibility ####
def has_some_source(profile):
    fields = ['source_profile', 'credential_source', 'credential_process']
    return any(profile.get(field) for field in fields)

def set_fake_profile(profiles, profile_name):
    fake_profile = f"{profile_name}_source_profile"
    profiles[profile_name]['source_profile'] = fake_profile
    profiles[fake_profile] = {}

def is_source_profile_registered(profiles, profile):
    return profiles.get(profile.get('source_profile'))

def is_profile_registered_in_1password_config(config, profile):
    return config.get('1password').get('profiles', {}).get(profile.get('source_profile'))
### END Manage AWS profiles and aws files ~/.aws/config ~/.aws/credentials compatibility ###
