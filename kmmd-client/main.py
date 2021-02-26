import os
import requests
from time import sleep
import ftplib


untouchables = []
work_dir = os.path.dirname(os.path.realpath(__file__))
path_to_config = os.path.join(work_dir, 'config.cfg')


def make_qs(local: list, remote: list):
    upload = []
    delete = []
    for line in remote:
        if line not in local:
            upload.append(line)
    for line in local:
        if line not in remote:
            if line not in untouchables:
                delete.append(line)
    return delete, upload


def first_get(url, controller, role, content_dir):
    while True:
        try:
            req = requests.get(url)
            # print(req.json())
            time_mark = req.headers['Last-Modified']
        except Exception:
            continue
        else:
            do_work(controller, role, content_dir)
            return time_mark


def do_work(controller, role, content_dir):
    con = ftplib.FTP(controller)
    con.login()
    remote_list = con.nlst()
    local_list = os.listdir(content_dir)
    delete_q, upload_q = make_qs(local_list, remote_list)
    if delete_q:
        if role == 'plasma':
            os.system('killall mpv')
        for line in delete_q:
            path = os.path.join(content_dir, line)
            print('removing %s' % line)
            os.remove(path)
    if upload_q:
        if role == 'plasma':
            os.system('killall mpv')
        for line in upload_q:
            path = os.path.join(content_dir, line)
            print('retrieving %s' % line)
            with open(path, 'wb') as file_in:
                con.retrbinary('RETR %s' % line, file_in.write)
    if role == 'plasma':
        if upload_q or delete_q:
            os.system('mpv --really-quiet --no-stop-screensaver \
                --loop-playlist --fullscreen %s > /dev/null 2>&1 \
                &' % content_dir)


def main():
    options = {}
    with open(path_to_config, 'r') as config:
        for line in config:
            line = line.strip()
            if not(line.startswith('#') or line == ''):
                key, val = line.split('=')
                options[key.strip()] = val.strip()
    controller = options['controller']
    role = options['role']
    content_dir = options['content_dir']
    if role == 'plasma':
        os.system('killall mpv')
        os.system('mpv --really-quiet --no-stop-screensaver --loop-playlist \
            --fullscreen %s > /dev/null 2>&1 &' % content_dir)
    url = 'http://%s/' % controller
    time_mark = first_get(url, controller, role, content_dir)
    while True:
        sleep(1)
        try:
            req = requests.head(url)
            if req.headers['Last-Modified'] != time_mark:
                req = requests.get(url)
                # print(req.json())
                do_work(controller, role, content_dir)
                time_mark = req.headers['Last-Modified']
            else:
                # print('no changes')
                pass
        except Exception:
            continue


if __name__ == '__main__':
    main()
