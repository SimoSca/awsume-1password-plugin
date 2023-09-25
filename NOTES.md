### PIPX UPDATE PLUGIN

`pipx` doesn't offers a way to update a plugin installed via `pipx inject`, so you can manually remove the plugin and reinstall it:

1. locate you plugin installation
2. remove the plugin `rm -rf ~/.local/pipx/venvs/awsume/lib/python3.10/site-packages/awsume_1password_plugin-X.x.y.dist-info`
3. reinstall the plugin `pipx inject awsume awsume-1password-plugin`
