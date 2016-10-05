import os
import json
from collections import OrderedDict as odict


class FileError(Exception):
    def __init__(self, desc):
        super(FileError, self).__init__(desc)


class ValidateError(Exception):
    def __init__(self, desc):
        super(ValidateError, self).__init__(desc)


def safe_mkdir(new_dir):
    if os.path.exists(new_dir):
        if not os.path.isdir(new_dir):
            raise FileError('{dir} is not a directory'.format(dir=new_dir))
    else:
        os.mkdir(new_dir)


def dump_to_json(data, file=None):
    params = {
        'ensure_ascii': False,
        'indent': 4,
        'sort_keys': not isinstance(data, odict),
    }
    if file:
        json.dump(data, file, **params)
        print(file=file)
    else:
        return json.dumps(data, **params)


def get_base_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_config(key=None, exp_keys=None):
    """Read and cache config file.

    key -- use to get certain part of the config,
    exp_keys -- use to check keys of that part of the config.
    """
    def validate_keys(keys, exp_keys):
        if exp_keys and len(set(exp_keys) ^ set(keys)) > 0:
            raise ValidateError('bad keys: {keys}, expected {exp_keys}'.format(
                keys=str(set(keys)), exp_keys=str(set(exp_keys))))

    # get data if it isn't done already
    config_file = os.path.join(get_base_dir(), 'config.json')
    if not get_config.config_data:
        if not os.path.isfile(config_file):
            raise FileError('config file {file} is not a regular file'.format(
                file=config_file))
        with open(config_file, 'r') as f:
            data = json.load(f)
        exp_keys_top = {'api_issue_cors', 'issue_template', 'github'}
        validate_keys(data.keys(), exp_keys_top)
        get_config.config_data = data
    # check and return a part of the config if given, full config otherwise
    if key:
        data = get_config.config_data[key]
        validate_keys(data.keys(), exp_keys)
        return data
    else:
        return get_config.config_data
get_config.config_data = None
