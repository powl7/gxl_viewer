from tkinter import *
from tkinter import ttk, filedialog
from PIL import ImageTk, Image

import networkx as nx

import sys
import os
import glob

import GraphConverter

def main():
    def is_image_file(filename):
        return filename.lower().endswith(('.png', '.bmp', '.jpg', '.jpeg', '.gif'))

    def get_image_file(path, name):
        for ending in ('png', 'bmp', 'jpg', 'jpeg', 'gif'):
            img_path = os.path.join(path, '{}.{}'.format(name, ending))
            if os.path.isfile(img_path):
                return img_path

    def is_gxl_file(filename):
        return filename.lower().endswith(('.gxl'))

    def select_img_dir(*args):
        new_dir = filedialog.askdirectory()
        if new_dir:
            if os.path.isdir(new_dir):
                img_dirname.set(new_dir)

    def select_gxl_dir(*args):
        new_dir = filedialog.askdirectory()
        if new_dir:
            if os.path.isdir(new_dir):
                change_gxl_dir(new_dir)
     
    def change_gxl_dir(new_dir):
        if os.path.isdir(new_dir):
            gxl_dirname.set(new_dir)
            listbox.delete(0, END)
            for f in sorted(os.listdir(new_dir)):
                if is_gxl_file(f):
                    filename = os.path.join(new_dir, f)
                    if os.path.isfile(filename):
                        listbox.insert('end', f.rsplit('.', 1)[0])
            listbox.select_set(0)
            onselect()


    def onselect(*args):
        canvas_image.delete("all")
        index = int(listbox.curselection()[0])
        value = listbox.get(index)
        print(value, gxl_dirname.get(), img_dirname.get())
        display_gxl_and_image(canvas=canvas_image, name=value, image_dir=img_dirname.get(), gxl_dir=gxl_dirname.get())


    def apply_offset(graph, width, height):
        offset_needed = False
        for n in graph:
            x, y = graph.node[n]['pos']
            if x < 0 or y < 0:
                offset_needed = True
                break

        if offset_needed:
            offset_x = width / 2
            offset_y = height / 2
            for n in graph:
                x, y = graph.node[n]['pos']
                graph.node[n]['pos'] = (x + offset_x, y + offset_y)

        return graph


    def display_gxl_and_image(canvas, name, image_dir, gxl_dir):
        img_filename = get_image_file(image_dir, name)
        myimg = ImageTk.PhotoImage(Image.open(img_filename))
        canvas.image = myimg
        canvas.create_image(0, 0, image=myimg, anchor=NW)
        
        if ((canvas.winfo_height() < myimg.height()) 
         or (canvas.winfo_width() < myimg.width())):
            # root.geometry('')
            canvas.config(height=myimg.height(), width=myimg.width())
        
        gxl_filename = os.path.join(gxl_dir, '{}.{}'.format(name, 'gxl'))
        g = GraphConverter.load_gxl_to_graph(gxl_filename)

        g = apply_offset(graph=g, height=myimg.height(), width=myimg.width())

        for n1 in g.edge:
            for n2 in g.edge[n1]:
                x1, y1 = g.node[n1]['pos']
                x2, y2 = g.node[n2]['pos']
                canvas.create_line(x1, y1, x2, y2, fill="red", width=1)
        for n in g:
            x, y = g.node[n]['pos']
            r = 2
            x1, y1 = (x - r), (y - r)
            x2, y2 = (x + r), (y + r)
            canvas.create_oval(x1, y1, x2, y2, outline="red", fill="red")

    root = Tk()
    root.title("Signature Graph Viewer")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    root.resizable(width=True, height=True)

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(2, weight=1)
    mainframe.rowconfigure(2, weight=1)
    mainframe.pack(expand=1, fill='both')

    img_dirname = StringVar()
    ttk.Button(mainframe, text='Image Path:', command=select_img_dir).grid(column=0, row=0, columnspan=2, sticky=(N, W))
    ttk.Label(mainframe, textvariable=img_dirname).grid(column=2, row=0, sticky=(N, W))

    gxl_dirname = StringVar()
    ttk.Button(mainframe, text='GXL Path:', command=select_gxl_dir).grid(column=0, row=1, columnspan=2, sticky=(N, W))
    ttk.Label(mainframe, textvariable=gxl_dirname).grid(column=2, row=1, sticky=(N, W))

    listbox = Listbox(mainframe, height=5)
    listbox.grid(column=0, row=2, sticky=(N,S))
    s = ttk.Scrollbar(mainframe, orient=VERTICAL, command=listbox.yview)
    s.grid(column=1, row=2, sticky=(N,S))
    listbox['yscrollcommand'] = s.set
    listbox.bind('<<ListboxSelect>>', onselect)

    canvas_image = Canvas(mainframe)
    # canvas_image.grid(column=2, row=2, columnspan=1, sticky=(N,E,S,W))
    canvas_image.grid(column=2, row=2, columnspan=1)
    # canvas_image['image'] = None
    # canvas_image.image = None

    for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)
    
    if len(sys.argv) == 2:
        input_gxl = sys.argv[1]
        input_img = os.path.join(os.path.dirname(os.path.normpath(input_gxl)), 'img')
        if not os.path.isdir(input_gxl):
            print(f'input_gxl does not exist: {input_gxl}')
            exit()
        if not os.path.isdir(input_img):
            print(f'input_img does not exist: {input_img}')
            exit()
        img_dirname.set(input_img)
        change_gxl_dir(input_gxl)

    # img_dirname.set('/Users/paul/DATA/data/MCYT-75/img/')
    # # change_gxl_dir('/Users/paul/DATA/data/MCYT-75/gxl-D25/')
    # change_gxl_dir('/Users/paul/DATA/data/MCYT-75/gxl-psm-s4/')

    # img_dirname.set('/Users/paul/DATA/data/CEDAR/img/')
    # change_gxl_dir('/Users/paul/DATA/data/CEDAR/gxl-D10/')
    # change_gxl_dir('/Users/paul/DATA/data/CEDAR/gxl-psm-s4/')

    # img_dirname.set('/Users/paul/DATA/data/UTSig/img/')
    # change_gxl_dir('/Users/paul/DATA/data/UTSig/gxl-D25/')

    # img_dirname.set('/Users/paul/DATA/data/MCYT-75/img/')
    # change_gxl_dir('/Users/paul/DATA/data/MCYT-75/gxl-D25-span3/')

    # img_dirname.set('/Users/paul/DATA/data/GPDS-75/img/')
    # change_gxl_dir('/Users/paul/DATA/data/GPDS-75/gxl-D25-span3/')

    listbox.focus()

    root.mainloop()


if __name__ == "__main__":
    main()
