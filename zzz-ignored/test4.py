import json


def extract_paths(data, parent_key='', result=None):
    if result is None:
        result = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            extract_paths(value, new_key, result)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_key = f"{parent_key}[{index}]"
            extract_paths(item, new_key, result)
    else:
        result.append(parent_key)

    return result


# Example usage
input_json = '''
{
    "attr1": "test",
    "individual": {
        "firstName": "lukasz",
        "lastName": "dupa"
    }
}
'''

data = json.loads(input_json)
paths = extract_paths(data)
for path in paths:
    print(path)
