from libdl import pls_run_thrgh, download
import sys


def local_file():
    from threading import Thread
    from serve import main as s

    server = Thread(target=s, args=())
    return server


def dl_local(rpc):
    rpc.start()
    pls_run_thrgh("http://localhost:8000/testfile1GB", path="testfile", recreate=True)
    rpc.join()
    sys.exit(1)


if __name__ == "__main__":
    # https://testfiledownload.com/
    # pls_run_thrgh('http://speedtest.ftp.otenet.gr/files/test10Mb.db')
    dl_local(local_file())
