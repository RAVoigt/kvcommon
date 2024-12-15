# KvCommon Python Utils

Library of miscellaneous common python utils that aren't worthy of their own dedicated libraries yet. Some of these packages will be moved out to their own libs later.

This library isn't likely to be useful to anyone else; it's just a convenience to save me from copy/pasting between various projects I work on.

# PyPi
https://pypi.org/project/kvcommon/

# Installation
### With Poetry:
`poetry add kvcommon`

### With pip:
`pip install kvcommon`

## Packages/Modules

| Package | Description | Example Usage |
|---|---|---|
|`datastore`|An abstraction for a simple dictionary-based key-value datastore with support for schema versions and files as 'backends' (TOML, YAML, etc.)|#TODO|
|`k8s`|Utils to reduce boilerplate when working with Kubernetes and GKE in Python|#TODO|
|`logger`|Boilerplate wrapper to get logger with formatting|`from kvcommon import logger as LOG; LOG.get_logger("logger_name")`|
|`misc`|Obligatory 'misc'
|`types`|Miscellaneous utils for either converting types or type-hinting|`from kvcommon import types; types.to_bool("false")`|
|`urls`|Convenience wrappers for URL parsing|`from kvcommon import types; types.to_bool("false")`|
