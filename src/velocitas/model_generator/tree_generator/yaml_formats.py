from ruamel.yaml import YAML

def format_units_yaml(yaml_file_path: str, parent_key: str, output_file_path: str):
    yaml = YAML()
    with open(yaml_file_path, 'r') as file:
        yaml_content = yaml.load(file)

    for _, value in yaml_content.items():
        if isinstance(value, dict) and 'unit' in value:
            value['label'] = value.pop('unit')

    formatted_units_yaml = {parent_key: yaml_content}

    with open(output_file_path, 'w') as output:
        yaml.dump(formatted_units_yaml, output)

# Example usage
# input_file = 'units_5.0.yaml'
# output_file = 'output.yaml'
# parent_key = 'units'