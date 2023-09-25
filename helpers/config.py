# Manage ~/.awsume/config.yaml: main plugin key is "1password"

def get_profile_settings_from_1password_config(config, profile_name):
    return config.get('1password', {}).get('profiles', {}).get(profile_name, {})