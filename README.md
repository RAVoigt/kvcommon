# KvCommon Python Utils

Library of miscellaneous common python utils that aren't worthy of their own dedicated libs.

## Configuration & Env Vars

| Env Var | Default|Description|
|---|---|---|
|`KVC_LOG_FORMAT`|`"%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"`|Sets log format for internal logger|
|`KVC_LOG_DATEFMT`|`"%Y-%m-%d %H:%M:%S"`|Sets log datetime format for internal logger|

## Packages/Modules

| Package | Description | Example Usage |
|---|---|---|
|`logger`|Boilerplate wrapper to get logger with formatting|`from kvcommon import logger as LOG; LOG.get_logger("logger_name")`|
|`datastore`|An abstraction for a simple dictionary-based key-value datastore with support for version for schema migrations and files as 'backends' (TOML, YAML, etc.)|#TODO|
|`types`|Miscellaneous utils for either converting types or type-hinting|`from kvcommon import types; types.to_bool("false")`|
