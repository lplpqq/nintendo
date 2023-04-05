import json
import os
import shutil
from json import JSONDecodeError
from typing import Union

from dataclass_factory import Factory, Schema
from requests.cookies import RequestsCookieJar
from loguru import logger

from nintendo import Nintendo, NintendoException, User


BASE_FOLDER_NAME = 'dumped'
if not os.path.exists(BASE_FOLDER_NAME):
    os.mkdir(BASE_FOLDER_NAME)


def get_all_cookies_files(folder_path: Union[str, os.PathLike]):
    cookies_files = []
    for root, dirs, files in os.walk(folder_path):
        cookies_files.extend(filter(lambda file_name: file_name.endswith('.txt'),
                              [os.path.join(root, file_name) for file_name in files]))
        for dir_name in dirs:
            cookies_files.extend(get_all_cookies_files(os.path.join(root, dir_name)))
    return cookies_files


def convert_netscape_to_json(netscape_cookies: str):
    cookie_list = []
    for cookie in netscape_cookies.split('\n'):
        cookie_dict = {}
        cookie_attrs = cookie.split('\t')
        if len(cookie_attrs) >= 7:
            cookie_dict['domain'] = cookie_attrs[0]
            cookie_dict['flag'] = cookie_attrs[1]
            cookie_dict['path'] = cookie_attrs[2]
            cookie_dict['secure'] = cookie_attrs[3] == 'TRUE'
            cookie_dict['expiration'] = cookie_attrs[4]
            cookie_dict['name'] = cookie_attrs[5]
            cookie_dict['value'] = cookie_attrs[6]
            cookie_list.append(cookie_dict)
    return cookie_list


def build_cookie_jar(cookie_file_path: Union[str, os.PathLike]):
    with open(cookie_file_path, encoding='latin-1') as file:
        content = file.read()

    try:
        cookie_list = json.loads(content)
    except JSONDecodeError:
        cookie_list = convert_netscape_to_json(content)

    cookie_jar = RequestsCookieJar()
    if cookie_list:
        try:
            for cookie in cookie_list:
                cookie_jar.set(cookie['name'], cookie['value'])
        except (TypeError, ValueError):
            return None
        return cookie_jar
    else:
        return None


def bulk_fetch(*cookies_files: Union[str, os.PathLike]):
    for cookies_file_path in cookies_files:
        cookie_jar = build_cookie_jar(cookies_file_path)

        if cookie_jar is None:
            logger.error(f'Failed to parse {os.path.basename(cookies_file_path)} cookies')
            continue

        logger.info(f"Logging in to account using {os.path.basename(cookies_file_path)} cookies")
        nintendo = Nintendo()
        try:
            authorization_code = nintendo.authorize(cookie_jar)
        except NintendoException:
            logger.error(f'Server refused authorization! {os.path.basename(cookies_file_path)} cookies are invalid')
        else:
            logger.success(f'Successfully logged in to using {os.path.basename(cookies_file_path)} cookies! '
                           f'Starting generating tokens...')

            nintendo.generate_tokens(authorization_code)
            logger.success(f'Successfully generated tokens using {os.path.basename(cookies_file_path)} cookies! '
                           f'Starting retrieving orders....')

            dump_factory = Factory(schemas={
                User: Schema(exclude=['obfuscated_id'])
            })

            user = User(profile=nintendo.profile, orders=[order for order in nintendo.retrieve_orders()])

            new_folder_name = f'{BASE_FOLDER_NAME}/{cookies_file_path.split(os.sep)[-2]}'
            try:
                os.mkdir(new_folder_name)
            except FileExistsError:
                pass
            shutil.copy2(cookies_file_path, new_folder_name)
            with open(f'{new_folder_name}/{nintendo.profile.obfuscated_id}.json', 'w', encoding='utf-8') as file:
                json.dump(dump_factory.dump(user), file, ensure_ascii=False, indent=4)

            logger.success(f'Fetching all orders has been done using {os.path.basename(cookies_file_path)} cookies! '
                           f'All the necessary data has been dumped to the {nintendo.profile.obfuscated_id}.json file')
