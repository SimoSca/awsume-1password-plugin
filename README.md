# Awsume 1Password Plugin

> The initial code was copied from [xeger](https://github.com/xeger/awsume-bitwarden-plugin). Thanks for this great starting point ❤️

This is a plugin that automates the entry of MFA tokens using 1Password.
It replaces AWSume's `MFA Token:` prompt with a biometric unlock and delegates to 1Password for policies on how often unlock is required.
In other words: it saves you from ever having to type an MFA token, ever again!

### Requirements

- _Awsume 4+_
- _1Password CLI_


## Installation

### Install This Plugin

```
pip3 install awsume-1password-plugin
```

If you've installed awsume with `pipx`, this will install the console plugin in awsume's virtual environment:

```
pipx inject awsume awsume-1password-plugin
```

### Set Up 1Password

1. Install the [1Password CLI](https://developer.1password.com/docs/cli)
2. Enable [biometric unlock](https://developer.1password.com/docs/cli/about-biometric-unlock) of the CLI in 1Password settings

### Configure AWSume

This plugin needs to know which 1Password vault item to use. You can specify this information in your AWSume configuration file:

```yaml
# ~/.awsume/config.yaml

colors: true
1password: 
  ...
  ...
  ...
```


## Features

The original design allowed **Multiple MFA Tokens** to be managed by mapping one or more `mfa_serials` (arn) via plugin configurations 
(file `~/.awsume/config.yaml` section `1password`) with aws profiles (file `~/.aws/config` section `profiles`).

Since version `1.3` support has also been introduced to retrieve login credentials (`access_key_id`` and `secret_access_key``) from 1password,
thus eliminating the need to save credentials in `~/.aws/credentials` (which is still possible to do, however).

Both options (mapping mfa or retrieving aws access keys) are valid and can be used in combination, 
especially the mfa_serial mapping specification wins over the aws profile specification (set in the awsume configuration file as specified below).

### Multiple MFA Tokens

Once you have added to a 1password vault your mfa with label `one-time password`, you can map the serial of the mfa to the vault title:

```yaml
# ~/.awsume/config.yaml

colors: true
fuzzy-match: false
1password:
  "arn:aws:iam::12345:mfa/tony": "AWS for Tony Inc."
  "arn:aws:iam::67890:mfa/xeger": "AWS for Xeger Enterprises"
```

This way the plugin will be able to retrieve the mfa token configured in the profile.

> It is important to note that in this case you will need to have properly configured the credentials on your pc
> for example in the `~/.aws/credentials` file, unless you use the second option described below.


### Multiple Profiles

It is possible to configure for each profile the title of a 1password vault in order to retrieve the login credentials via `op cli`,
this way you can stop saving aws access keys in `~/.aws/credentials`, and you can possibly avoid using `source_profile` in `~/.aws/config`:

```yaml
# ~/.awsume/config.yaml
1password:
  profiles:
    simosca_acount_xxx_api:
      title: "<AWS for SimoSca Inc.>"
```

this way 1password plugin is able to figure out for a given profile from which vault to retrieve the login credentials.
As above, we have some constraints:

- for aws access key id the labels `access key id`, `access_key_id`, `aws access key id` and `aws_access_key_id` are allowed.
- for aws secret access key the labels `secret access key`, `secret_access_key`, `aws secret access key`, and `aws_secret_access_key` are allowed
- for mfa the label `one-time password` is allowed.

#### Avoid source_profile

Without `source_profile` in the configurations you can define the `profiles.<your_profile>` and automatically the plugin will create in awsume (internally to the process) a `<your_profile>_source_profile` profile, but it is necessary that you define it in `1password.profiles`: this way it can set the credentials of your `fake` profile.

So if in `~/.aws/config` you have defined a `simosca_acount_xxx_api` profile without `source_profile` or other sources such as `credential_source` or `credential_process`, in `~/.awsume/config.yaml` you will need to enter:

```yaml
1password:
  profiles:
    simosca_acount_xxx_api_source_profile:
      title: "<AWS for SimoSca Inc.>"
```

#### Virtual source_profile

You can continue to use `source_profile` and avoid populating the file `~/.aws/credentials`: you just map your generic `source_profile` with the profile you defined in `1password.profiles` and then the plugin will inject the credentials of this profile (always retrieved via 1password cli) similarly to what you saw above:

```yaml
1password:
  profiles:
    simosca_acount_yyy_another_profile:
      title: "<AWS for SimoSca Another Profile Inc.>"
```

where the profile defined in `~/.aws/config` is `simosca_acount_yyy_another_profile`.



## Usage

This plugin works automatically in the background; just `awsume` roles as you normally would, and it will invoke the `op` command to obtain TOTP tokens whenever AWSume requires one.

## Troubleshooting

If you experience any trouble, invoke `awsume` with the `--debug` flag and look for log entries that contain `1password`.

The specific command that this plugin invokes is `op item get --otp "One password title"`; make sure it succeeds when you invoke it manually.

