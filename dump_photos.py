import configparser
import functools
import json
import re
import vk_api
import vk_api.messages


def json_to_str(obj):
    return json.dumps(obj, ensure_ascii=False, indent=4)


def collect_links(links_out, message):
    def _parse_links(str):
        str = re.sub(r'<.*>', ' ', str)
        return re.findall(r'\S+\w\.[a-zA-Zа-яёА-ЯЁ]\S+', str)

    for str in ['url', 'body', 'text', 'description']:
        if str in message:
            links = _parse_links(message[str])
            if not links:
                continue
            owner_id = None
            for id_str in ['owner_id', 'copy_owner_id', 'from_id', 'uid']:
                if id_str in message:
                    owner_id = message[id_str]
            date = message.get('date', None)
            if (not owner_id or not date) and str != 'url':
                print('WARNING: message has not owner_id or date information: ', json_to_str(message))
            links_out.append({
                'owner_id': owner_id,
                'links': links,
                'created':  date
            })
    if 'type' in message and message['type'] != 'audio':
        collect_links(links_out, message[message['type']])


def collect_photos(photos_out, message):
    if 'photo' not in message:
        return
    for src in ['src_xxxbig', 'src_xxbig', 'src_xbig', 'src_big', 'src', 'src_small']:
        if src in message['photo']:
            photos_out.append({
                'owner_id': message['photo']['owner_id'],
                'src': message['photo'][src],
                'created':  message['photo']['created']
            })
            return


def main():
    config = configparser.ConfigParser()
    config.read(['default_config.ini', 'config.ini'])

    app_id = config.get('application', 'id')
    app_secret_key = config.get('application', 'secret_key')

    client = vk_api.Client(app_id, app_secret_key, ['messages', 'photos'])

    data_arr = []
    for item in client.get_messages():
        links, photos = [], []
        vk_api.messages.process_item(item, functools.partial(collect_links, links), fwd_messages=True)
        vk_api.messages.process_attachments(item, functools.partial(collect_links, links), fwd_messages=True)
        vk_api.messages.process_attachments(item, functools.partial(collect_photos, photos), fwd_messages=True)
        if links or photos:
            data_arr.append({
                'date': item['date'],
                'uid': item['uid'],
                'links': links,
                'photos': photos
            })

    data_dict = {}
    for item in data_arr:
        for link_item in item['links']:
            data_dict_link_items = []
            for link in link_item['links']:
                data_dict_link_items.append({
                    'link': link,
                    'created': link_item['created']
                })
            uid = item['uid']
            owner_id = link_item['owner_id'] if link_item['owner_id'] else 'unknown'

            data_dict.setdefault(uid, {}).setdefault(owner_id, []).extend(data_dict_link_items)

        for photo_item in item['photos']:
            data_dict_photo_item = {
                'src': photo_item['src'],
                'created': photo_item['created']
            }
            uid = item['uid']
            owner_id = photo_item['owner_id']

            data_dict.setdefault(uid, {}).setdefault(owner_id, []).append(data_dict_photo_item)

    print(json_to_str(data_dict))


if __name__ == "__main__":
    main()
