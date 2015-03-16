# Readme

This repository contains a script to create an authors publication list by  querying the [NASA ADS][ADS]. The output will be either LaTeX (just `\items` or a complete document) or the compiled PDF.

The script can automatically include citation counts (`-c`) or open access information (`-oa`).

The [NASA ADS][ADS] query uses the [ADS developper API][API] for which you will need a dev key. The key needs to be specified by the option `-d` or as environment variable `ADS_DEV_KEY`. If you don't have a key, see [here](https://github.com/adsabs/adsabs-dev-api#signup--access).

The script assumes the combination of first initial and last name to be a unique author. If this is not the case, you can further filter the results by ADS database (for example only `astronomy`). If this is not enough you need to modify the script yourself.

For more description about the available options, call the help using the `-h` option.

[ADS]: http://adsabs.harvard.edu
[API]: https://github.com/adsabs/adsabs-dev-api