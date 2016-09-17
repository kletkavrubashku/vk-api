import configparser
import functools
import json
import re
import vk_api
import vk_api.messages


def json_to_str(obj):
    return json.dumps(obj, ensure_ascii=False, indent=4, sort_keys=True)


def collect_links(links, message):
    def _parse_links(str):
        return re.findall(r'\S+\w\.[a-zA-Zа-яёА-ЯЁ]\S+', str)

    for str in ['body', 'text', 'url', 'description']:
        if str in message:
            links += _parse_links(message[str])
    if 'type' in message:
        collect_links(links, message[message['type']])


def main():
    config = configparser.ConfigParser()
    config.read(['default_config.ini', 'config.ini'])

    app_id = config.get('application', 'id')
    app_secret_key = config.get('application', 'secret_key')

    client = vk_api.Client(app_id, app_secret_key, ['messages', 'photos'])

    links = []
    for item in client.get_messages():
        vk_api.messages.process_item(item, functools.partial(collect_links, links), fwd_messages=True)
        vk_api.messages.process_attachments(item, functools.partial(collect_links, links), fwd_messages=True)
        print(json_to_str(item))
    print(links)


if __name__ == "__main__":
    main()
