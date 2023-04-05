import glob
import json
import os
from threading import Thread
from typing import Union

from loguru import logger

from utils import bulk_fetch


def main(threads_number: int, cookies_folder_path: Union[str, os.PathLike]):
    cookies_files = glob.glob(os.path.join(cookies_folder_path, '**/*.txt'))
    if cookies_files:
        logger.debug(f'{len(cookies_files)} cookie files were loaded!')
    else:
        logger.critical(f'No cookie files were loaded!')
        return

    threads = {}
    for i in range(min(threads_number, len(cookies_files))):
        threads[i] = []

    for data_number in range(len(cookies_files)):
        thread_id = data_number % threads_number
        threads[thread_id].append(cookies_files[data_number])

    for k, cookies_files in threads.items():
        Thread(target=bulk_fetch,
               args=(*cookies_files, )).start()
        logger.info(f'Thread number {k + 1} started')


def cli():
    """Wrapper for command line"""

    def read_config(config_path: str = "config.json"):
        with open(config_path) as file:
            return dict(json.load(file).items())

    try:
        logger.error("Script started!\n")
        main(**read_config())
    except (KeyboardInterrupt, SystemExit):
        logger.error("\nScript stopped!")


if __name__ == "__main__":
    cli()
