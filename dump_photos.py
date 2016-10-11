import configparser
import datetime
import functools
import json
import os
import re
import urllib.request
import vk_api
import vk_api.messages

OUTPUT_DIR_NAME = 'output'
LINKS_FILE_NAME = 'links.html'


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
            date = message.get('date', message.get('created', None))
            if (not owner_id or not date) and str != 'url':
                print('WARNING: message has not owner_id or date information: ', json_to_str(message))
            links_out.append({
                'owner_id': owner_id,
                'links': links,
                'date':  date
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
                'date':  message['photo']['created']
            })
            return


def uid_to_name(client, uid):
    if not isinstance(uid, int):
        return uid
    if uid > 0:
        user = client.get_users(user_ids=[uid], caching=True)[0]
        return '{} {}'.format(user['first_name'], user['last_name'])
    else:
        group = client.get_groups(group_ids=[-uid], caching=True)[0]
        return group['name']


def main():
    config = configparser.ConfigParser()
    config.read(['default_config.ini', 'config.ini'])

    app_id = config.get('application', 'id')
    app_secret_key = config.get('application', 'secret_key')

    client = vk_api.Client(app_id, app_secret_key, ['messages', 'photos'])

    data_arr = []
    for out in [0]:
        if out == 0:
            print('Get inbox messages...')
        else:
            print('Get outbox messages...')
        messages = client.get_messages(out=out)
        for n, item in enumerate(messages):
            if n % 100 == 0:
                print('\t{} from {}'.format(n, len(messages)))

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

    print('Resolve names...')
    data_dict = {}
    for n, item in enumerate(data_arr):
        if n % 20 == 0:
            print('\t{} from {}'.format(n, len(data_arr)))
        for link_item in item['links']:
            data_dict_link_items = []
            for link in link_item['links']:
                data_dict_link_items.append({
                    'link': link,
                    'date': datetime.datetime.fromtimestamp(link_item['date']).strftime('%Y-%m-%d %H:%M:%S') if link_item['date'] else None
                })
            u_name = '{} ({})'.format(uid_to_name(client, item['uid']), item['uid'])
            owner_name = '{} ({})'.format(uid_to_name(client, link_item['owner_id']), link_item['owner_id'])

            data_dict.setdefault(u_name, {}).setdefault(owner_name, []).extend(data_dict_link_items)

        for photo_item in item['photos']:
            data_dict_photo_item = {
                'src': photo_item['src'],
                'name': datetime.datetime.fromtimestamp(photo_item['date']).strftime('IMG_%Y%m%d_%H%M%S.jpg')
            }
            u_name = '{} ({})'.format(uid_to_name(client, item['uid']), item['uid'])
            owner_name =  '{} ({})'.format(uid_to_name(client, photo_item['owner_id']), photo_item['owner_id'])

            data_dict.setdefault(u_name, {}).setdefault(owner_name, []).append(data_dict_photo_item)

    print('Save files...')
    if not os.path.exists(OUTPUT_DIR_NAME):
        os.makedirs(OUTPUT_DIR_NAME)
    for key, value in data_dict.items():
        print('\t{}'.format(key))
        dir = os.path.join(OUTPUT_DIR_NAME, key)
        if not os.path.exists(dir):
            os.makedirs(dir)
        for key1, value1 in value.items():
            dir1 = os.path.join(dir, key1)
            if not os.path.exists(dir1):
                os.makedirs(dir1)
            links = []
            for i in value1:
                if 'src' in i:
                    urllib.request.urlretrieve(i['src'], os.path.join(dir1, i['name']))
                else:
                    links.append('{0} <a href="{1}">{1}</a>'.format(i['date'], i['link']))
            if links:
                links.sort()
                with open(os.path.join(dir1, LINKS_FILE_NAME), 'w') as f:
                    f.write('<br>'.join(links))

if __name__ == '__main__':
    main()
