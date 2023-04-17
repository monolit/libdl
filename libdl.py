import requests
import argparse
import sys
# import tqdm
from tqdm.rich import trange
import time
import os
import datetime
import traceback
from urllib.parse import unquote
import warnings

warnings.filterwarnings("ignore")

CHUNK_SIZE = 1024 * 1024  # 1024KB
AVERAGE_SPEED_WINDOW = 5  # window size to calculate average download speed in seconds

# https://github.com/kiriharu/zerochan/blob/main/zerochan/__main__.py#L26


def super_duper_logger(text: str, level="FILEINFO"):
    """This is my secret development, shh!"""
    print(f"[{datetime.datetime.now()}] [{level}]: {text}")


def ensure_directory_exists(directory_path):
    """
    Ensures that the specified directory exists. If it doesn't exist, creates it.

    Args:
        directory_path: The path of the directory to ensure existence of.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        print(f"Created directory {directory_path}")


def get_name(url):
    name = url.rstrip("/")
    for delimiter, index in [["/", -1], ["&", 0], ["?", 0]]:
        name = name.split(delimiter)[index]
    name = unquote(name)
    for letter in ["/", "\\"]:
        name = name.replace(letter, "_")
    return name


def humanize_size(size):
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f'{size:.1f} {unit}'
        size /= 1024.0
    return f'{size:.1f} TB'


def download(
    url, path=os.getcwd(), recreate=False, _quiet=False, filename=None, headers=None
):
    """
    Downloads a file from the given URL to the specified path.

    :param url: The URL to download the file from.
    :type url: str
    :param path: The path to save the downloaded file to.
    :type path: str
    :param recreate: Whether to recreate the file if it already exists.
    :type recreate: bool, optional
    :param quiet: Whether to suppress output to the console.
    :type quiet: bool, optional
    :param filename: The name to save the downloaded file as. If not provided, the last part of the URL is used.
    :type filename: str, optional
    :param headers: Any additional headers to include in the request.
    :type headers: dict, optional

    :raises requests.exceptions.HTTPError: If the server returns an error status code.

    :return: filename
    """
    if headers is None:
        headers = {}
    ensure_directory_exists(path)
    if not filename:
        filename = get_name(url)
    filepath = os.path.join(path, filename)
    server_bytes = int(
        requests.head(url, timeout=7, headers=headers).headers.get(
            "Content-Length")
    )

    if os.path.exists(filepath):
        local_bytes = os.path.getsize(filepath)
        if local_bytes < server_bytes:
            # resume download from the last byte
            headers["Range"] = f"bytes={local_bytes}-"
            filemode = "ab"
            super_duper_logger(
                f"Resuming download! {filename} from {humanize_size(local_bytes)} to {humanize_size(server_bytes)}"
            )
        elif recreate:
            super_duper_logger({"status": "recreating file"})
            filemode = "wb"
        elif local_bytes == server_bytes:
            super_duper_logger({"status": "Skipping as already complete"})
            return filename
        else:
            super_duper_logger(
                f"""{filename} error but you can try:
                local {local_bytes} not server {server_bytes}""")
            # raise NotImplementedError
            return None # filename
    else:
        local_bytes = 0
        filemode = "wb"
    need_bytes = server_bytes - local_bytes
    # with tqdm.tqdm(server_bytes, unit="B", unit_divisor=1024, unit_scale=True, ncols=100) as pbar:
    with trange(server_bytes, unit="B", unit_divisor=1024, unit_scale=True, ncols=1000) as pbar:
        pbar.update(local_bytes)
        pbar.set_description(f"{filename}")
        start_time = time.time()
        downloaded_size = 0
        avg_speeds = []

        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(filepath, filemode) as f:
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    f.write(chunk)
                    pbar.update(len(chunk))
                    downloaded_size += len(chunk)
                    if downloaded_size >= need_bytes:
                        super_duper_logger(
                            f"Skipping as already complete:\
                            local {local_bytes + downloaded_size} and server {server_bytes}")
                        return filename
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    download_speed = downloaded_size / elapsed_time
                    if (
                        len(avg_speeds) == 0
                        or current_time - AVERAGE_SPEED_WINDOW < avg_speeds[-1][1]
                    ):
                        avg_speeds.append((download_speed, current_time))
                    else:
                        while (
                            avg_speeds
                            and current_time - AVERAGE_SPEED_WINDOW > avg_speeds[0][1]
                        ):
                            avg_speeds.pop(0)
                        avg_speeds.append((download_speed, current_time))
                    if avg_speeds:
                        avg_speed = round(
                            sum(speed for speed, _ in avg_speeds)
                            / len(avg_speeds)
                        )
                        pbar.set_postfix(
                            {"avg_speed": humanize_size(avg_speed) + "/s"})
        super_duper_logger(f"Downloaded {filename} to {path}", "DOWNLOADER")
    return filename


def pls_run_thrgh(smth=None, **kwargs):
    """
    don't mind that so

    simpliest and configured way for easy download

    """
    desc = "Simple command-line script to ..."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "url",
        nargs="*",
        default=[smth],
        help="may be string with spaces, e. g. url1 url2",
    )
    args = parser.parse_args()
    # hardcoded because fuck you
    max_attempts = 2
    attempts = 1
    while 0 < attempts < max_attempts:
        try:
            for url in args.url:
                if url is not None:
                    print(url)
                    if not (l := kwargs.get("path")):
                        path = os.getcwd()
                    else:
                        path = l
                        del kwargs["path"]
                    download(url, path=path, **kwargs)
                # future fails
                attempts = 1
            break
        except requests.exceptions.ConnectionError:
            sys.exit("ну всё, допинговался и умир")
        except Exception as error:
            traceback.print_exception(
                type(error), error, error.__traceback__, limit=1)
            # print(error)
            attempts += 1
            # bruh why
            attempts = max(attempts, 0)

        except KeyboardInterrupt:
            sys.exit("exiting, see ya")


if __name__ == "__main__":
    pls_run_thrgh()
