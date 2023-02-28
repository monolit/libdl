import requests
import argparse
import sys
import tqdm
import time
import os
import datetime
import traceback

CHUNK_SIZE = 1024 * 1024  # 1024KB
AVERAGE_SPEED_WINDOW = 5  # window size to calculate average download speed in seconds

# https://github.com/kiriharu/zerochan/blob/main/zerochan/__main__.py#L26


def super_duper_logger(text: str, level: str):
    """This is my secret development, shh!"""
    print(f"[{datetime.datetime.now()}] [{level}]: {text}")


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        print(f"Created directory {directory_path}")
    else:
        print(f"Directory {directory_path} already exists")


def download(url, path, recreate=False, quiet=False, filename=None, headers=None):
    if headers is None:
        headers = {}
    ensure_directory_exists(path)
    if not filename:
        filename = url.split("/")[-1]
    filepath = os.path.join(path, filename)
    server_bytes = int(
        requests.head(url, timeout=7, headers=headers).headers["Content-Length"]
    )
    if not quiet:
        with tqdm.tqdm(
            total=server_bytes, unit="B", unit_scale=True, ncols=100
        ) as pbar:
            pbar.set_description(f"Downloading {filename}")
            start_time = time.time()
            downloaded_size = 0
            avg_speeds = []
            if os.path.exists(filepath):
                local_bytes = os.path.getsize(filepath)
                if local_bytes < server_bytes:
                    # resume download from the last byte
                    headers["Range"] = f"bytes={local_bytes}-"
                    filemode = "ab"
                    pbar.update(local_bytes)
                    super_duper_logger(
                        f"Resuming download! {filename} from {round(local_bytes / 1024)}kb to {round(server_bytes / 1024)}kb",
                        "FILEINFO",
                    )
                elif recreate:
                    pbar.set_postfix({"status": "recreating file"})
                    filemode = "wb"
                else:
                    pbar.set_postfix({"status": "Skipping as already complete"})
                    return
            else:
                filemode = "wb"
            with requests.get(url, headers=headers, stream=True) as r:
                r.raise_for_status()
                with open(filepath, filemode) as f:
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        f.write(chunk)
                        pbar.update(len(chunk))
                        downloaded_size += len(chunk)
                        current_time = time.time()
                        elapsed_time = current_time - start_time
                        download_speed = downloaded_size / elapsed_time
                        pbar.set_postfix(
                            {
                                "speed": "{:.2f} B/s".format(download_speed),
                                "time_left": str(
                                    datetime.timedelta(
                                        seconds=(server_bytes - downloaded_size)
                                        / download_speed
                                    )
                                ),
                            }
                        )
                        if (
                            len(avg_speeds) == 0
                            or current_time - AVERAGE_SPEED_WINDOW < avg_speeds[-1][1]
                        ):
                            avg_speeds.append((download_speed, current_time))
                        else:
                            while (
                                avg_speeds
                                and current_time - AVERAGE_SPEED_WINDOW
                                > avg_speeds[0][1]
                            ):
                                avg_speeds.pop(0)
                            avg_speeds.append((download_speed, current_time))
                        if avg_speeds:
                            avg_speed = round(
                                sum(speed for speed, _ in avg_speeds)
                                / len(avg_speeds)
                                / 1024
                            )
                            pbar.set_postfix(
                                {"avg_speed": "{:.2f} KB/s\n".format(avg_speed)}
                            )
            super_duper_logger(f"Downloaded {filename} to {path}", "DOWNLOADER")
        return print()


def pls_run_thrgh(smth=None, **kwargs):
    desc = "Simple command-line script to ..."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("url", nargs="*", default=[smth])
    args = parser.parse_args()
    # hardcoded because fuck you
    max_attempts = 2
    attempts = 1
    while attempts < max_attempts and attempts > 0:
        try:
            for url in args.url:
                if url is not None:
                    print(url)
                    if not (l := kwargs.get("path")):
                        path = os.getcwd()
                    else:
                        path = l
                        del kwargs["path"]
                    download(url, path=path, quiet=False, **kwargs)
                # future fails
                attempts = 1
            break
        except requests.exceptions.ConnectionError as e:
            sys.exit(f"ну всё, допинговался")
        except Exception as error:
            traceback.print_exception(type(error), error, error.__traceback__, limit=1)
            # print(error)
            attempts += 1
            # bruh why
            if attempts < 0:
                attempts = 0

        except KeyboardInterrupt:
            sys.exit("exiting, see ya")


if __name__ == "__main__":
    # https://speed.hetzner.de/100MB.bin /1GB /10GB
    # https://testfiledownload.com/
    # pls_run_thrgh('http://speedtest.ftp.otenet.gr/files/test10Mb.db')

    pls_run_thrgh("http://localhost:8000/testfile1GB", path="testfile", recreate=True)
