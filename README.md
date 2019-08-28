# Minecraft Advancements Twitch extension
All the different components of the Minecraft Advancement Tracker extension for Twitch.

Contents:

* `extension/` The code for the Twitch extension itself
  * `extension/public/` The front-end code for the extension panel (HTML/JS)
  * Currently the extension does not use a backend service
* `client/` The client-side process for monitoring the Minecraft save data (Python)
* `www/` The external web components, mostly to be an in-between for Twitch OAuth so that the secret token doesn't need to be in the client (PHP)
* `assets/` Some miscellaneous source files, images, etc that get built into the other components. Minecraft spritesheets and various icon formats.

See [the full installation instructions](https://www.mrphlip.com/mc_twitchext/) for more information about using this.
