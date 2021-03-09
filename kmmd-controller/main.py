import os
from time import sleep


work_dir = os.path.dirname(os.path.realpath(__file__))
content_dir = os.path.join(work_dir, 'content')
path_to_pl = os.path.join(work_dir, 'clients', 'playlist')
restart_flag = 'restart_req'


while True:
    if restart_flag in os.listdir(content_dir):
        os.rmdir(os.path.join(content_dir, restart_flag))
        with open(path_to_pl, 'w') as playlist:
            for line in os.listdir(content_dir):
                if not line.startswith('.'):
                    print(line, file=playlist)
    sleep(1)
