import os
import sys
import subprocess
from threading import Thread
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.ttk import *
from tkinter.messagebox import askokcancel
import ftplib


formats = ['mp4', 'mov', 'avi', 'webm', 'mkv']
web_server = '192.168.100.100'
kmmd_server = '192.168.100.1'
untouchables = []


class Base():

    def __init__(self):
        self.root_directory = ''
        self.no_start = ''
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.pre_check()
        self.create_gui()

    def create_gui(self):
        self.root = Tk()
        self.root.title('KMMD')
        self.root.resizable(False, False)

        Style().configure("WF.TFrame", relief=GROOVE)

        self.canvas = Canvas(
            self.root, highlightthickness=0, width=400, height=400,
        )
        self.canvas.pack(fill=BOTH)
        self.create_intro_window()
        self.root.mainloop()

    def choose_directory(self):
        self.root_directory = askdirectory()
        self.root_label.configure(text=self.root_directory)
        if self.root_directory:
            self.convert_button_web.config(state=NORMAL)
            self.convert_button_plasma.config(state=NORMAL)
            self.deliver_button_web.config(state=NORMAL)
            self.deliver_button_plasma.config(state=NORMAL)

    def pre_check(self):
        if 'nt' in sys.builtin_module_names:
            cmd = 'where'
        else:
            cmd = ''
        if cmd:
            try:
                subprocess.check_call(
                    [cmd, 'ffmpeg'],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except Exception:
                self.no_start = 'ffmpeg not found'
            else:
                self.no_start = ''
        else:
            self.no_start = 'OS is not Windows'

    def create_intro_window(self):
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.canvas.delete('message')
        if self.no_start:
            label_head = Label(self.canvas, text='Sorry:')
            self.canvas.create_window(200, 80, window=label_head, tag='intro')
            label_error = Label(self.canvas, text=self.no_start)
            self.canvas.create_window(
                200, 120, window=label_error, tag='intro'
            )
        else:
            choose_button = Button(
                self.canvas, text='Choose directory',
                command=self.choose_directory
            )
            self.canvas.create_window(
                200, 20, window=choose_button, tag='intro'
            )
            self.root_label = Label(self.canvas, text=self.root_directory)
            self.canvas.create_window(
                200, 60, window=self.root_label, tag='intro'
            )
            if not self.root_directory:
                init_state = DISABLED
            else:
                init_state = NORMAL
            self.convert_button_web = Button(
                self.canvas, text='Convert videos for web',
                command=lambda: self.call_converter('web'), state=init_state
            )
            self.canvas.create_window(
                200, 120, window=self.convert_button_web, tag='intro'
            )
            self.convert_button_plasma = Button(
                self.canvas, text='Convert videos for plasma and tkiosk',
                command=lambda: self.call_converter('plasma'), state=init_state
            )
            self.canvas.create_window(
                200, 160, window=self.convert_button_plasma, tag='intro'
            )
            self.deliver_button_web = Button(
                self.canvas, text='Deliver videos to web',
                command=lambda: self.get_cred('web'), state=init_state
            )
            self.canvas.create_window(
                200, 220, window=self.deliver_button_web, tag='intro'
            )
            self.deliver_button_plasma = Button(
                self.canvas, text='Deliver videos to plasma and tkiosk',
                command=lambda: self.get_cred('plasma'), state=init_state
            )
            self.canvas.create_window(
                200, 260, window=self.deliver_button_plasma, tag='intro'
            )

    def create_message_window(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.canvas.delete('intro')
        message_window = Frame(self.canvas, style='WF.TFrame')
        message_scrollbar = Scrollbar(message_window)
        self.message_text = Text(
            message_window, state="disabled", highlightthickness=0,
            bd=0, yscrollcommand=message_scrollbar.set
        )
        self.canvas.create_window(
            0, 0, anchor=NW, window=message_window, width=400, height=360,
            tag='message'
        )
        message_scrollbar.pack(side=RIGHT, fill=Y)
        self.message_text.pack(side=LEFT, fill=BOTH)
        message_scrollbar.config(command=self.message_text.yview)

        self.back_button = Button(
            self.canvas, text='Back', command=self.create_intro_window,
            state=DISABLED
        )
        self.canvas.create_window(
            200, 380, window=self.back_button, tag='message'
        )

    def put_message(self, *text):

        text = '\n' + ' '.join([str(line) for line in text])
        self.message_text.configure(state='normal')
        self.message_text.insert(END, text)
        self.message_text.configure(state='disabled')
        self.message_text.see(END)
        self.root.update()

    def call_converter(self, opt):
        self.create_message_window()
        if opt == 'web':
            Thread(target=self.convert_files_for_web).start()
        elif opt == 'plasma':
            Thread(target=self.convert_files_for_plasma).start()

    def get_cred(self, opt):
        cred_frame = Frame(self.canvas, style='WF.TFrame')
        self.canvas.create_window(
            200, 200, window=cred_frame, tag='cred_frame'
        )
        header = 'Deliver to '
        if opt == 'web':
            header += 'web'
        elif opt == 'plasma':
            header += 'plasma and tkiosk'
        header_label = Label(cred_frame, text=header)
        header_label.pack(pady=20)
        login = StringVar()
        login_label = Label(cred_frame, text='Login')
        login_label.pack()
        login_input = Entry(cred_frame, textvariable=login)
        login_input.pack()
        password = StringVar()
        password_label = Label(cred_frame, text='Password')
        password_label.pack()
        password_input = Entry(
            cred_frame, show='*', textvariable=password
        )
        password_input.pack()
        button_frame = Frame(cred_frame)
        button_frame.pack(pady=20, padx=20)
        back_button = Button(
            button_frame, text='Back',
            command=cred_frame.destroy
        )
        back_button.pack(side=LEFT)
        next_button = Button(
            button_frame, text='Next',
            command=lambda: self.call_delivery(
                opt, cred_frame, (login.get(), password.get())
            )
        )
        next_button.pack(side=LEFT)
        cred_frame.grab_set()

    def call_delivery(self, opt, frame, cred):
        frame.destroy()
        self.create_message_window()
        if opt == 'web':
            Thread(
                target=self.deliver_files_to_web,
                args=(cred[0], cred[1])
            ).start()
        elif opt == 'plasma':
            Thread(
                target=self.deliver_files_to_plasma,
                args=(cred[0], cred[1])
            ).start()

    def on_closing(self):
        if askokcancel('Quit', 'Do you want to quit program?'):
            try:
                self.p.kill()
            except Exception:
                pass
            self.root.destroy()

    def convert_files_for_web(self):
        folders = os.listdir(self.root_directory)
        for i in folders:
            path_i = os.path.join(self.root_directory, i)
            if not os.path.isdir(path_i):
                self.put_message('%s is not a dir' % i)
            else:
                self.put_message('%s' % i)
                work_dir = path_i
                files = os.listdir(work_dir)
                point = 1
                for n in files:
                    work_file = os.path.join(work_dir, n)
                    file_name = n.split('.')[0].split('_')[0]
                    self.put_message(n[:20], '...')
                    if (n.split('.')[-1] in formats) and (file_name != i):
                        try:
                            bitrate = subprocess.check_output(
                                [
                                    'ffprobe', '-loglevel', 'quiet', '-v',
                                    'error', '-select_streams', 'v:0',
                                    '-show_entries', 'stream=bit_rate', '-of',
                                    'default=noprint_wrappers=1', work_file
                                ], creationflags=subprocess.CREATE_NO_WINDOW
                            )
                            bitrate = int(
                                bitrate.decode('utf-8').split('=')[-1]
                            )
                            if bitrate > 2000000:
                                bitrate = 2000000
                        except Exception:
                            self.put_message(
                                '\tException caught in get_bitrate, \
    using 2000K'
                            )
                            bitrate = 2000000
                        bitrate = str(bitrate // 1000) + 'K'
                        self.put_message('\twebm')
                        # make webm
                        out = i + "_" + str(point) + ".webm"
                        out = os.path.join(work_dir, out)
                        self.p = subprocess.Popen(
                            [
                                "ffmpeg", '-y', '-loglevel', 'quiet', '-i',
                                work_file, '-deadline', 'realtime',
                                '-cpu-used', '5', '-c:v', 'libvpx', '-b:v',
                                bitrate, '-b:a', '144K', out
                            ], creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        self.p.wait()
                        self.put_message('\tmp4')
                        # make mp4
                        out = i + "_" + str(point) + ".mp4"
                        out = os.path.join(work_dir, out)
                        self.p = subprocess.Popen(
                            [
                                "ffmpeg", '-y', '-loglevel', 'quiet', '-i',
                                work_file, '-threads', '4', '-preset',
                                'superfast', '-b:v', bitrate, '-b:a',
                                '144K', out
                            ], creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        self.p.wait()
                        self.put_message('\tsshot')
                        # find half of duration
                        try:
                            time = subprocess.check_output(
                                [
                                    'ffprobe', '-loglevel', 'quiet', '-v',
                                    'error', '-show_entries',
                                    'format=duration', '-of',
                                    'default=noprint_wrappers=1:nokey=1',
                                    work_file
                                ], creationflags=subprocess.CREATE_NO_WINDOW
                            )
                            time = str(float(time.decode('utf-8')) / 2)
                        except Exception:
                            self.put_message(
                                '\tException in find_half_duration, using 10s'
                            )
                            time = '10'

                        '''
                        make screenshot at half of duration and check
                        its size to avoid black screen
                        '''
                        vol = 1
                        out = i + "_" + str(point) + ".jpg"
                        out = os.path.join(work_dir, out)
                        while True:
                            # set_crop
                            try:
                                with subprocess.Popen(
                                    [
                                        'ffmpeg', '-i', work_file, '-ss',
                                        time, '-t', '1',
                                        '-vf', 'cropdetect', '-f', 'null', '-'
                                    ],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    universal_newlines=True,
                                    creationflags=subprocess.CREATE_NO_WINDOW
                                ) as crop_proc:
                                    for line in crop_proc.stdout:
                                        if 'crop' in line:
                                            line = line.split()[-1].split(
                                                '='
                                            )[-1]
                                            if int(line.split(':')[1]) > 0:
                                                crop = line
                                crop = 'crop=' + crop
                            except Exception:
                                self.put_message('\tException in set_crop!')
                                crop = ''
                            cmd = [
                                'ffmpeg', '-loglevel', 'quiet', '-ss',
                                time, '-i', work_file, '-q:v', '2',
                                '-vframes', '1'
                            ]
                            if crop:
                                cmd.append('-vf')
                                cmd.append(crop)
                            cmd.append(out)
                            # print(cmd)
                            try:
                                self.p = subprocess.Popen(
                                    cmd,
                                    creationflags=subprocess.CREATE_NO_WINDOW
                                )
                                self.p.wait()
                            except Exception:
                                self.put_message(
                                    'Error on screen shot, adding time'
                                )
                                count = vol * pow(-1, vol)
                                time = str(float(time) + count * 1)
                                vol += 1
                                continue
                            if os.path.getsize(out) > 50000:
                                break
                            os.remove(out)
                            count = vol * pow(-1, vol)
                            time = str(float(time) + count * 1)
                            vol += 1
                        # delete input
                        os.remove(work_file)
                        self.put_message('\t\tDone')
                        point += 1
                    else:
                        self.put_message(
                            '"%s" in "%s" looks like output of this \
    converting script or input is not a video \
    file.' % (n, i)
                        )
                self.put_message('.........................')
        self.put_message('All files were converted')
        self.back_button.config(state=NORMAL)

    def convert_files_for_plasma(self):
        folder_raw = self.root_directory
        if 'converted' in os.path.basename(folder_raw):
            self.put_message(
                'Source directory is named converted, rename it \
or choose another source'
            )
        else:
            folder_conv = os.path.join(
                os.path.dirname(self.root_directory), 'converted'
            )
            self.put_message('')
            files = os.listdir(folder_raw)
            if not os.path.exists(folder_conv):
                os.mkdir(folder_conv)
                self.put_message('Created directory "converted"')
            else:
                self.put_message('Found directory "converted"')
            for n in files:
                if n.split('.')[-1] in formats:
                    self.put_message(n)
                    '''
                    check bitrate of input and make it 2000K or
                    leave it the same
                    '''
                    name = os.path.join(folder_raw, n)
                    try:
                        bitrate = subprocess.check_output(
                            [
                                'ffprobe', '-loglevel', 'quiet', '-v',
                                'error',
                                '-select_streams', 'v:0', '-show_entries',
                                'stream=bit_rate', '-of',
                                'default=noprint_wrappers=1', name
                            ], creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        bitrate = int(
                            bitrate.decode('utf-8').split('=')[-1]
                        )
                        if bitrate > 2050000:
                            bitrate = 2050000
                    except Exception:
                        self.put_message(
                            '\tException caught in get_bitrate, \
using 2000K'
                        )
                        bitrate = 2000000

                    bitrate = str(bitrate // 1000) + 'K'
                    out = n.split('.')[0] + '.' + "mp4"
                    out = os.path.join(folder_conv, out)
                    fs = "scale=1280:720:force_original_aspect_ratio=1,\
                                pad=1280:720:(ow-iw)/2:(oh-ih)/2"
                    self.p = subprocess.Popen(
                        [
                            "ffmpeg", '-y', '-loglevel', 'quiet', '-i',
                            name,
                            "-vf", fs, '-threads', '4', '-preset',
                            'superfast', '-b:v', bitrate, '-b:a', '144K',
                            out
                        ], creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    self.p.wait()
                    self.put_message("\tDone")
                else:
                    self.put_message("%s is not a video file" % n)
            self.put_message('All files were converted')
        self.back_button.config(state=NORMAL)

    def delivery_worker(self, login, password, server):
        try:
            con = ftplib.FTP(server)
        except Exception as e:
            self.put_message(
                "Error connecting to %s: %s, " % (server, e)
            )
            return None
        else:
            try:
                con.login(user=login, passwd=password)
            except Exception as e:
                self.put_message(
                    "Error connecting to %s: %s, " % (server, e)
                )
                return None
            else:
                return con

    def deliver_files_to_plasma(self, login, password):

        def make_qs(local: list, remote: list):
            upload = []
            delete = []
            for line in local:
                if line not in remote:
                    upload.append(line)
            for line in remote:
                if line not in local:
                    if line not in untouchables:
                        delete.append(line)
            return delete, upload

        local_list = os.listdir(self.root_directory)
        faulty = []
        for i in local_list:
            if i.split('.')[-1] not in formats:
                self.put_message(
                    '%s is not a video file, check source directory.' % i
                )
                faulty.append(i)
        if not faulty:
            server = kmmd_server
            self.put_message("delivering to kmmd-server %s" % server)
            connect = self.delivery_worker(login, password, server)
            if connect:
                remote_list = connect.nlst()
                delete_q, upload_q = make_qs(local_list, remote_list)
                if delete_q:
                    self.put_message('Delete in process..')
                    for line in delete_q:
                        self.put_message(line)
                        try:
                            connect.delete(line)
                        except Exception as e:
                            self.put_message(
                                'Error deleting file %s: %s' % (line, e)
                            )
                else:
                    self.put_message('Nothing to delete')
                if upload_q:
                    self.put_message('Transfer in process..')
                    for line in upload_q:
                        try:
                            self.put_message(line)
                            path = os.path.join(self.root_directory, line)
                            with open(path, 'rb') as file_in:
                                connect.storbinary(
                                    cmd='STOR %s' % line, fp=file_in
                                )
                        except Exception as e:
                            self.put_message(
                                'Error sending file %s: %s' % (line, e)
                            )
                else:
                    self.put_message('Nothing to upload')
                if upload_q or delete_q:
                    try:
                        connect.mkd('restart_req')
                    except Exception as e:
                        self.put_message(
                            'Error creating dir restart_req: %s' % e
                        )
                connect.quit()
                self.put_message("Connection closed")
        else:
            self.put_message("Problem with source files detected")
        self.back_button.config(state=NORMAL)

    def deliver_files_to_web(self, login, password):
        folders_list = os.listdir(self.root_directory)
        faulty = []
        for i in folders_list:
            if i.isdigit():
                if int(i) > 5000000:
                    continue
                else:
                    faulty.append(i)
                    self.put_message("%s doesn't look like '5315312'" % i)
            else:
                faulty.append(i)
                self.put_message("%s doesn't look like '5315312'" % i)
        if not faulty:
            server = web_server
            self.put_message("delivering to web-server %s" % server)
            connect = self.delivery_worker(login, password, server)
            if connect:
                for folder in folders_list:
                    try:
                        connect.mkd(folder)
                        self.put_message("creating folder %s" % folder)
                    except Exception as e:
                        self.put_message(
                            'Error creating dir %s: %s' % (folder, e)
                        )
                    else:
                        connect.cwd(folder)
                        path_folder = os.path.join(self.root_directory, folder)
                        for line in os.listdir(path_folder):
                            path_file = os.path.join(path_folder, line)
                            try:
                                with open(path_file, 'rb') as in_file:
                                    connect.storbinary(
                                        cmd='STOR %s' % line, fp=in_file
                                    )
                                self.put_message("sending %s" % line)
                            except Exception as e:
                                self.put_message(
                                    'Error sending file %s: %s' % (line, e)
                                )
                        connect.cwd('..')
                connect.quit()
                self.put_message("Connection closed")
        else:
            self.put_message("Problem with source files detected")
        self.back_button.config(state=NORMAL)


if __name__ == '__main__':
    conv_del = Base()
