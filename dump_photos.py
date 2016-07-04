import configparser
import vk_api
import json

def main():
    config = configparser.ConfigParser()
    config.read(['default_config.ini', 'config.ini'])

    app_id = config.get('application', 'id')
    app_secret_key = config.get('application', 'secret_key')

    client = vk_api.Client(app_id, app_secret_key, ['messages', 'photos'])

    messages = client.get_messages()
    for item in messages:
        response = json.dumps(item, ensure_ascii=False, indent=4, sort_keys=True)
        print(response)

if __name__ == "__main__":
    main()
