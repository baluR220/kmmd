'''
Wrapper over youtube-dl for fancy gui. Yotube-dl module required,
install it with 'pip install youtube-dl'.

'''
import traceback
import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askokcancel
from threading import Thread


no_ydl_module = False
try:
    import youtube_dl
except Exception:
    no_ydl_module = True


class Base():

    def __init__(self):
        self.root_directory = ''
        root = tk.Tk()
        root.title('YDL')
        root.resizable(False, False)

        ttk.Style().configure("WF.TFrame", background='white',
                              relief=tk.GROOVE)
        ttk.Style().configure("Red.TLabel", foreground='red')

        canvas = tk.Canvas(
            root, highlightthickness=0, width=400, height=240,
        )
        canvas.pack(fill=tk.BOTH)
        self.create_intro_window(root, canvas)
        root.mainloop()

    def choose_directory(self, label, button):
        '''
        Ask user for path to save file.
        '''
        self.root_directory = askdirectory()
        label.configure(text=self.root_directory)
        if self.root_directory:
            button.configure(state=tk.NORMAL)

    def create_intro_window(self, root, canvas):
        '''
        Create main window.
        '''
        root.protocol("WM_DELETE_WINDOW", root.destroy)
        canvas.delete('message')
        if not no_ydl_module:
            url = tk.StringVar()
            link_label = ttk.Label(canvas, text='Link to download:')
            canvas.create_window(200, 20, window=link_label, tag='intro')
            link_entry = ttk.Entry(canvas, width=50,
                                   textvariable=url)
            canvas.create_window(200, 50, window=link_entry, tag='intro')
            link_entry.focus_set()
            link_error = ttk.Label(canvas, text='',
                                   style='Red.TLabel')
            canvas.create_window(
                200, 80, window=link_error, tag='intro'
            )
            choose_button = ttk.Button(
                canvas, text='Save to:',
                command=lambda: self.choose_directory(root_label,
                                                      download_button)
            )
            canvas.create_window(
                200, 110, window=choose_button, tag='intro'
            )
            root_label = ttk.Label(canvas)
            canvas.create_window(
                200, 140, window=root_label, tag='intro'
            )
            download_button = ttk.Button(
                canvas, text='Download',
                state=tk.DISABLED,
                command=lambda: self.download_file(root, canvas,
                                                   url, link_error)
            )
            canvas.create_window(
                200, 200, window=download_button, tag='intro'
            )
        else:
            error_label = ttk.Label(
                canvas,
                text='youtube_dl module not found, \
try "pip install youtube_dl"'
            )
            canvas.create_window(200, 50, window=error_label, tag='intro')

    def create_message_window(self, root, canvas):
        '''
        Create message window with status of download.
        '''
        root.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(root))
        canvas.delete('intro')
        message_window = ttk.Frame(canvas, style='WF.TFrame')
        message_scrollbar = ttk.Scrollbar(message_window)
        message_text = tk.Text(
            message_window, state="disabled", highlightthickness=0,
            bd=0, yscrollcommand=message_scrollbar.set
        )
        canvas.create_window(
            0, 0, anchor=tk.NW, window=message_window, width=400, height=200,
            tag='message'
        )
        message_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        message_text.pack(side=tk.LEFT, fill=tk.BOTH)
        message_scrollbar.config(command=message_text.yview)

        self.back_button = ttk.Button(
            canvas, text='Back',
            command=lambda: self.create_intro_window(root, canvas),
            state=tk.DISABLED
        )
        canvas.create_window(
            200, 220, window=self.back_button, tag='message'
        )
        return message_text

    def put_message(self, text_object, *text):
        '''
        Put message in specified text_object.
        '''
        text_object.configure(state='normal')
        text = ' '.join(text)
        text = '\n' + text
        text_object.insert(tk.END, text)
        text_object.configure(state='disabled')
        text_object.see(tk.END)

    def download_thread(self, text_object, url):
        '''
        Thread with youtube_dl working.
        '''

        def progress_hook(data):
            '''
            Function to show download status.
            '''
            nonlocal text_object
            if data['status'] == 'downloading':
                progress = data['_percent_str']
                text_object.configure(state='normal')
                text_object.delete('end-1l linestart', tk.END)
                text_object.configure(state='disabled')
                text_object.see(tk.END)
                self.put_message(text_object, progress)
            if data['status'] == 'finished':
                self.put_message(text_object, 'Done.')

        name = f'%(title)s.%(ext)s'
        out_path = os.path.join(self.root_directory, name)
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': out_path,
            'progress_hooks': [progress_hook],
        }
        url = url.get()
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                self.put_message(text_object, 'Started downloading..')
                info = ydl.extract_info(url, download=False)
                try:
                    self.put_message(
                        text_object,
                        '%s.%s' % (info['title'], info['ext'])
                    )
                except Exception:
                    self.put_message(text_object,
                                     'Exception in printing file name')
                self.put_message(text_object,
                                 'Destination:', self.root_directory)
                self.put_message(text_object, ' ')
                ydl.download([url])
                self.back_button.configure(state=tk.NORMAL)
        except Exception:
            self.put_message(text_object, traceback.format_exc())
            self.back_button.configure(state=tk.NORMAL)
        finally:
            self.back_button.configure(state=tk.NORMAL)

    def download_file(self, root, canvas, url, label):
        '''
        Wrapper over download thread.
        '''
        if url.get():
            text_object = self.create_message_window(root, canvas)
            Thread(target=self.download_thread,
                   daemon=True, args=(text_object, url)).start()
        else:
            label.configure(text='Specify link!')

    def on_closing(self, root):
        '''
        Function to be called when specified as protocol for
        root close window event.
        '''
        if askokcancel('Quit', 'Do you want to quit program?'):
            root.destroy()


if __name__ == '__main__':
    downloader = Base()
