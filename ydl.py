from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.ttk import *
from threading import Thread
from tkinter.messagebox import askokcancel
import traceback
import os


no_ydl_module = False
try:
    import youtube_dl
except Exception:
    no_ydl_module = True


class Base():

    def __init__(self):
        self.root_directory = ''
        self.root = Tk()
        self.root.title('YDL')
        self.root.resizable(False, False)

        Style().configure("WF.TFrame", background='white', relief=GROOVE)
        Style().configure("Red.TLabel", foreground='red')

        self.canvas = Canvas(
            self.root, highlightthickness=0, width=400, height=240,
        )
        self.canvas.pack(fill=BOTH)
        self.create_intro_window()
        self.root.mainloop()

    def choose_directory(self):
        self.root_directory = askdirectory()
        self.root_label.configure(text=self.root_directory)
        if self.root_directory:
            self.download_button.configure(state=NORMAL)

    def create_intro_window(self):
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.canvas.delete('message')
        if not no_ydl_module:
            self.url = StringVar()
            link_label = Label(self.canvas, text='Link to download:')
            self.canvas.create_window(200, 20, window=link_label, tag='intro')
            link_entry = Entry(self.canvas, width=50, textvariable=self.url)
            self.canvas.create_window(200, 50, window=link_entry, tag='intro')
            link_entry.focus_set()
            self.link_error = Label(self.canvas, text='', style='Red.TLabel')
            self.canvas.create_window(
                200, 80, window=self.link_error, tag='intro'
            )
            choose_button = Button(
                self.canvas, text='Save to:', command=self.choose_directory
            )
            self.canvas.create_window(
                200, 110, window=choose_button, tag='intro'
            )
            self.root_label = Label(self.canvas)
            self.canvas.create_window(
                200, 140, window=self.root_label, tag='intro'
            )
            self.download_button = Button(
                self.canvas, text='Download',
                command=self.download_file, state=DISABLED
            )
            self.canvas.create_window(
                200, 200, window=self.download_button, tag='intro'
            )
        else:
            error_label = Label(
                self.canvas,
                text='youtube_dl module not found, \
try "pip install youtube_dl"'
            )
            self.canvas.create_window(200, 50, window=error_label, tag='intro')

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
            0, 0, anchor=NW, window=message_window, width=400, height=200,
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
            200, 220, window=self.back_button, tag='message'
        )

    def put_message(self, *text):
        self.message_text.configure(state='normal')
        text = ' '.join(text)
        text = '\n' + text
        self.message_text.insert(END, text)
        self.message_text.configure(state='disabled')
        self.message_text.see(END)
        self.root.update()

    def progress_hook(self, data):
        if data['status'] == 'downloading':
            progress = data['_percent_str']
            self.message_text.configure(state='normal')
            self.message_text.delete('end-1l linestart', END)
            self.message_text.configure(state='disabled')
            self.message_text.see(END)
            self.root.update()
            self.put_message(progress)
        if data['status'] == 'finished':
            self.put_message('Done.')

    def download_thread(self):
        name = f'%(title)s.%(ext)s'
        out_path = os.path.join(self.root_directory, name)
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': out_path,
            'progress_hooks': [self.progress_hook],
        }
        url = self.url.get()
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                self.put_message('Started downloading..')
                info = ydl.extract_info(url, download=False)
                try:
                    self.put_message(
                        '%s.%s' % (info['title'], info['ext'])
                    )
                except Exception:
                    self.put_message('Exception in printing file name')
                self.put_message('Destination:', self.root_directory)
                self.put_message(' ')
                ydl.download([url])
                self.back_button.configure(state=NORMAL)
        except Exception:
            self.put_message(traceback.format_exc())
            self.back_button.configure(state=NORMAL)
        finally:
            self.back_button.configure(state=NORMAL)

    def download_file(self):
        if self.url.get():
            self.create_message_window()
            Thread(target=self.download_thread, daemon=True).start()
        else:
            self.link_error.configure(text='Specify link!')

    def on_closing(self):
        if askokcancel('Quit', 'Do you want to quit program?'):
            self.root.destroy()


if __name__ == '__main__':
    downloader = Base()
