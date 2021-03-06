import jsonschema
import json
import pkg_resources
import yaml
from timeseries_etl.utils import field_type_check

# loading in all of the kafka schema here to avoid constantly reloading it
resource_package = __name__
kafka_msg_schema_stream = pkg_resources.resource_stream(resource_package, '/'.join(('schemas', 'kafka-message.schema.json')))
kafka_msg_schema = json.load(kafka_msg_schema_stream)
kafka_msg_schema_stream.close()


def validate_kafka_messsage(msg: dict, schema=kafka_msg_schema):
    """

    :param msg: loaded json message to validate
    :param schema: schema to validate against
    :return: boolean
    """
    jsonschema.validate(msg, schema, format_checker=jsonschema.FormatChecker())

    # validate field types
    for key, val in msg.items():
        if key[0] == '_':
            continue
        try:
            field_type_check(val['value'], val['type'])
        except Exception:
            print('Failed to validate field types on value = {}, type = {}'.format(val['value'], val['type']))  # TODO change to log this
            raise

    return True


def validate_transform_config(msg):
    """

    :param msg: loaded yaml message to validate
    :return: boolean
    """
    transform_config_schema = __load_schema('transform_configuration.schema.yaml')
    jsonschema.validate(msg, transform_config_schema)

    return True


def validate_loader_config(msg):
    """

    :param msg: loaded yaml message to validate
    :return: boolean
    """

    transform_config_schema = __load_schema('loader_configuration.schema.yaml')
    jsonschema.validate(msg, transform_config_schema)

    return True


def validate_extractor_config(msg):

    transform_config_schema = __load_schema('extractor_configuration.schema.yaml')
    jsonschema.validate(msg, transform_config_schema)

    return True

def __load_schema(schema_filename):
    """

    :param schema_filename: the name of the file in the schemas directory
    :return: loaded file
    """
    rel_path_to_schema = '/'.join(('schemas', schema_filename))
    transform_config_stream = pkg_resources.resource_stream(resource_package, rel_path_to_schema)
    transform_config_schema = yaml.load(transform_config_stream)
    transform_config_stream.close()

    return transform_config_schema