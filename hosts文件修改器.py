'''
张泊桥于2024年2月27日创建
用时4小时
'''


import ctypes
from tkinter.messagebox import askyesno,showerror,showinfo,askyesnocancel
from tkinter import simpledialog
from tkinter import *
from tkinter.ttk import Button
import sys
import win32api
import os
from tkinter.filedialog import asksaveasfilename,askopenfilename
from tkinter.ttk import Treeview
from typing import Literal
from easy_tool import run_function_from_thread

window = None


def aboutme():
    a = Toplevel(root)
    a.resizable(False,False)
    a.title("About - 关于")
    Label(a,text="创作者 : \nPorchcup",font=("Consolas","20")).grid(row=0,column=0)
    p = PhotoImage(file="yjtp1.png")
    Label(a,image=p).grid(row=0,column=1,padx=20,pady=20)
    Label(a,text="版本号：1.0",font=("Consolas","25")).grid(row=1,column=0,columnspan=2)
    a.mainloop()

def setting():
    global window
    b = Toplevel(root)
    window = b
    Label(b,text="默认hosts文件路径：").grid(row=0,column=0)
    e = Entry(b,width=30)
    e.grid(row=0,column=1)
    e.delete(0,END)
    e.insert(END,hostslocation)
    Button(b,text="浏览",command=lambda:asklocat(e)).grid(row=0,column=2)
    Label(b,text="自动备份文件路径：").grid(row=1,column=0)
    e1 = Entry(b,width=30)
    e1.grid(row=1,column=1)
    e1.delete(0,END)
    e1.insert(END,backuplocation)
    Button(b,text="浏览",command=lambda:asklocat_default(e1)).grid(row=1,column=2)
    Button(b,text="确定",command=lambda:write_setting(hosts=e.get(),backup=e1.get())).grid(row=2,column=0,columnspan=3)
    b.mainloop()

def write_setting(**kwargs):
    f = open("settings.txt","w",encoding="utf-8")
    f.write(str(kwargs))
    f.close()
    global hostslocation,backuplocation
    r = read_setting()
    hostslocation = r["hosts"]
    backuplocation = r["backup"]
    window.destroy()

def read_setting():
    end = ""
    f = open("settings.txt","r",encoding="utf-8")
    end = eval(f.read())
    f.close()
    return end


def asklocat(entry:Entry):
    a = askopenfilename(title="选择文件")
    if a != None and a != "":
        if os.path.split(a)[-1] == "hosts":
            entry.delete(0,END)
            entry.insert(END,a)
        else:
            showerror("错误","选择错误，应选择hosts文件。")

def asklocat_default(entry:Entry):
    a = asksaveasfilename(title="备份文件保存于")
    if a != None and a != "":
        entry.delete(0,END)
        entry.insert(END,a)


def askstring(title,prompt):
    ask = simpledialog.askstring(title,prompt)
    if ask == '' or ask == None:
        return 0
    else:
        return ask


def isadmin():
    return ctypes.windll.shell32.IsUserAnAdmin()


def add():
    ask = askstring("请输入","请输入要限制的网址（不包含https://）")
    showinfo("提示","即将ping该网站，ping操作可能需要一定的时间，请稍等。")
    result = os.popen(f"ping {ask}").read()
    codes = ["找不到主机","往返行程的估计时间","请求超时"]
    if codes[1] in result:
        add_network(selectip(),ask)
    else:
        if askyesno("注意","错误：{}，是否添加？".format(codes[0] if codes[0] in result else codes[2])):
            add_network(selectip(),ask)


def selectip():
    if open_autobackup.get():
        auto_backup()
    back = ''
    while True:
        ask = askyesnocancel("请选择","请选择一个ip地址，如果一个没用可以换另一个：\n是：127.0.0.1\n否：0.0.0.0\n取消：自定义")
        if ask == True:
            back =  "127.0.0.1"
        elif ask == False:
            back = "0.0.0.0"
        elif ask == None:
            ask = askstring("请输入","请输入ip地址：")
            result = os.popen(f"ping {ask}").read()
            codes = ["找不到主机","往返行程的估计时间","请求超时"]
            if codes[1] in result:
                back = ask
            else:
                if askyesno("注意","错误：{}，是否添加？".format(codes[0] if codes[0] in result else codes[2])):
                    back = ask
        if back != '':
            break
    return back


def add_network(ip,net):
    info_list.append(ip+" "+net)
    update()
    showinfo("注意",f"添加网站{net}成功")


def update():
    clear()
    for i in range(len(info_list)):
        t.insert("",i,values=(info_list[i].split(" ")[0],info_list[i].split(" ")[1]))

def delete():
    if open_autobackup.get():
        auto_backup()
    if len(t.selection()) != 0 :
        info_list.remove(get())
        update()
        showinfo("提示","删除成功")
    else:
        ask = askstring("请输入","请输入要删除的网址：")
        for i in range(len(info_list)):
            if ask == info_list[i].split(" ")[-1]:
                info_list.remove(info_list[i])
                update()
                showinfo("提示","删除成功")
                return 0
        showerror("错误","未发现该网址，请核对网址后重试")
        
def write():
    auto_backup()
    if askyesno("注意","您将要覆盖的文件为：%s\n此操作会彻底覆盖系统文件，确定执行此操作吗？"%hostslocation):
        new = infos+info_list
        try:
            fi = open(hostslocation,"w",encoding="utf-8")
            fi.write("\n".join(new))
            fi.close()
        except PermissionError:
            showerror("错误","无权限访问文件，请使用管理员身份再次运行。")
        showinfo("提示","写hosts文件成功")


def backupp():
    ask = asksaveasfilename()
    fi = open(hostslocation,"r",encoding="utf-8")
    bcup = open(ask,"w",encoding="utf-8")
    bcup.write(fi.read())
    fi.close()
    bcup.close()
    showinfo("提示","备份成功")

def recovery():
    auto_backup()
    ask = askopenfilename()
    if askyesno("注意","您将要覆盖的文件为：%s\n此操作会彻底覆盖系统文件，确定执行此操作吗？"%hostslocation):
        try:
            fi = open(hostslocation,"w",encoding="utf-8")
            bcup = open(ask,"r",encoding="utf-8")
            fi.write(bcup.read())
            fi.close()
            bcup.close()
            read()
            update()
            showinfo("提示","恢复成功")
        except PermissionError:
            showerror("错误","无权限打开文件，请使用管理员身份再次运行。")

def read(undo:bool|None=False):
    global file,info,info_list,infos
    if undo != True:
        file = open(hostslocation if undo == False else backuplocation,"r",encoding="utf-8")
        info = file.read()
        file.close()
    else:
        info = bak
    info_list = []
    infos = []
    for i in info.split("\n"):
        if len(i) != 0 and not info.split("\n")[0]==i:
            if i[0]!='#':
                info_list.append(i)
            else:
                infos.append(i)
        else:
            infos.append(i)
    for i in range(len(info_list)):
        info_list[i] = info_list[i].replace("\t"," ")

def clear():
    t.delete(*t.get_children())

def get():
    foc = t.focus()
    print(' '.join(list(t.set(foc).values())))
    return ' '.join(list(t.set(foc).values()))

def clear_focus():
    t.selection_remove(*t.selection())

def replace_ip(event=None):
    if open_autobackup.get():
        auto_backup()
    if len(t.selection()) != 0 :
        a = askstring("请输入","请输入更改后的ip地址")
        if a == 0:
            return 0
        else:
            result = os.popen(f"ping {a}").read()
            codes = ["找不到主机","往返行程的估计时间","请求超时"]
            if codes[1] in result:
                info_list[info_list.index(get())] = a + ' ' + get().split(" ")[1]
                alert("change")
            else:
                if askyesno("注意","错误：{}，是否添加？".format(codes[0] if codes[0] in result else codes[2])):
                    info_list[info_list.index(get())] = a + ' ' + get().split(" ")[1]
                    alert("change")
        update()
    else:
        showinfo("注意","请选中ip项")


def alert(alert_type=Literal["add","del","change"]):
    types = {"add":"添加","del":"删除","change":"修改"}
    showinfo("提示","{}成功".format(types[alert_type]))

def open_hosts():
    run_function_from_thread(lambda:os.system("notepad "+hostslocation),True)

def auto_backup_write():
    global bak
    file = open(hostslocation,"r",encoding="utf-8")
    bak = file.read()
    file.close()

def auto_backup(alert:bool=False):
    new = infos+info_list
    fi = open(backuplocation,"w",encoding="utf-8")
    fi.write("\n".join(new))
    fi.close()
    if alert:
        showinfo("提示","手动备份成功！")

def undo_write():
    ans = askyesno("提示","该功能用于撤销之前的写入或恢复操作，且撤销并不会自动写入而是刷新，是否继续？")
    if ans:
        read(True)
        update()

def undo():
    auto_backup()
    read(None)
    update()

bak = ""
if not os.path.exists("settings.txt"):
    fi = open("settings.txt","w",encoding="utf-8")
    fi.write('{"hosts":"%s","backup":"backup.txt"}'%(os.popen("echo %windir%").read().strip("\n")+"\\System32\\drivers\\etc\\hosts"))
    fi.close()
if not isadmin():
    if askyesno("注意","本程序需要足够的权限以访问系统文件，是否要以管理员权限重新运行？"):
        win32api.ShellExecute(None,"runas", sys.executable, __file__, None, 1)
    else:
        hostslocation = read_setting()["hosts"]
        backuplocation = read_setting()["backup"]
        root = Tk()
        root.iconbitmap("write.ico")
        root.title("hosts文件修改器")
        open_autobackup = IntVar()
        open_autobackup.set(1)
        read()
        auto_backup()
        l = Listbox(root,width=50)
        t = Treeview(root,show="headings",columns=("ip地址","网站"))
        t.column("ip地址",width=100)
        t.column("网站",width=300)
        t.heading("ip地址",text="ip地址")
        t.heading("网站",text="网站")
        t.grid(row=0,column=0,rowspan=8)
        clear()
        for i in range(len(info_list)):
            t.insert("",i,values=(info_list[i].split(" ")[0],info_list[i].split(" ")[1]))
        exec("l.insert(0,{})".format(','.join(['\"'+i+'\"' for i in info_list])))
        #l.grid(row=0,column=0,rowspan=5)
        s = Scrollbar(root)
        t.config(yscrollcommand=s.set)
        t.bind("<Double-1>",replace_ip)
        s.config(command=t.yview)
        s.grid(row=0,column=1,rowspan=8,ipady=90)
        menubar = Menu(root)
        filemenu = Menu(menubar, tearoff=False)
        filemenu.add_command(label="写入",command=write)
        filemenu.add_command(label="打开hosts文件",command=open_hosts)
        filemenu.add_command(label="撤销写入",command=undo_write)
        filemenu.add_separator()
        filemenu.add_command(label="备份",command=backupp)
        filemenu.add_command(label="恢复",command=recovery)
        controlmenu = Menu(menubar,tearoff=0)
        controlmenu.add_command(label="撤销/重做",command=undo)
        controlmenu.add_command(label="手动一键备份",command=lambda:auto_backup(True))
        controlmenu.add_checkbutton(label="操作前自动备份",onvalue=1,offvalue=0,variable=open_autobackup)
        menubar.add_cascade(label="文件", menu=filemenu)
        menubar.add_cascade(label="操作",menu=controlmenu)
        editmenu = Menu(menubar, tearoff=False)
        editmenu.add_command(label="添加",command=add)
        editmenu.add_command(label="删除",command=delete)
        editmenu.add_command(label="更改",command=replace_ip)
        menubar.add_cascade(label="ip地址", menu=editmenu)
        see = Menu(menubar,tearoff=False)
        see.add_command(label="清除焦点",command=clear_focus)
        see.add_command(label="刷新",command=update)
        menubar.add_cascade(label="视图",menu=see)
        about = Menu(menubar,tearoff=False)
        about.add_command(label="设置",command=setting)
        about.add_command(label="关于",command=aboutme)
        about.add_command(label="退出",command=exit)
        menubar.add_cascade(label="帮助",menu=about)
        root.config(menu=menubar)
        '''
        Button(root,text="添加",command=add).grid(row=0,column=2)
        Button(root,text="更改ip地址",command=replace_ip).grid(row=1,column=2)
        Button(root,text="删除",command=delete).grid(row=2,column=2)
        Button(root,text="写入",command=write).grid(row=3,column=2)
        Button(root,text="备份",command=backup).grid(row=4,column=2)
        Button(root,text="恢复",command=recovery).grid(row=5,column=2)
        Button(root,text="清除焦点",command=clear_focus).grid(row=6,column=2)
        Button(root,text="打开hosts",command=open_hosts).grid(row=7,column=2)
        '''
        root.mainloop()
else:
    hostslocation = read_setting()["hosts"]
    backuplocation = read_setting()["backup"]
    root = Tk()
    root.iconbitmap("write.ico")
    root.title("hosts文件修改器")
    open_autobackup = IntVar()
    open_autobackup.set(1)
    read()
    auto_backup()
    l = Listbox(root,width=50)
    t = Treeview(root,show="headings",columns=("ip地址","网站"))
    t.column("ip地址",width=100)
    t.column("网站",width=300)
    t.heading("ip地址",text="ip地址")
    t.heading("网站",text="网站")
    t.grid(row=0,column=0,rowspan=8)
    clear()
    for i in range(len(info_list)):
        t.insert("",i,values=(info_list[i].split(" ")[0],info_list[i].split(" ")[1]))
    exec("l.insert(0,{})".format(','.join(['\"'+i+'\"' for i in info_list])))
    #l.grid(row=0,column=0,rowspan=5)
    s = Scrollbar(root)
    t.config(yscrollcommand=s.set)
    t.bind("<Double-1>",replace_ip)
    s.config(command=t.yview)
    s.grid(row=0,column=1,rowspan=8,ipady=90)
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=False)
    filemenu.add_command(label="写入",command=write)
    filemenu.add_command(label="打开hosts文件",command=open_hosts)
    filemenu.add_command(label="撤销写入",command=undo_write)
    filemenu.add_separator()
    filemenu.add_command(label="备份",command=backupp)
    filemenu.add_command(label="恢复",command=recovery)
    controlmenu = Menu(menubar,tearoff=0)
    controlmenu.add_command(label="撤销",command=undo)
    controlmenu.add_command(label="手动一键备份",command=auto_backup)
    controlmenu.add_checkbutton(label="操作前自动备份",onvalue=1,offvalue=0,variable=open_autobackup)
    menubar.add_cascade(label="文件", menu=filemenu)
    menubar.add_cascade(label="操作",menu=controlmenu)
    editmenu = Menu(menubar, tearoff=False)
    editmenu.add_command(label="添加",command=add)
    editmenu.add_command(label="删除",command=delete)
    editmenu.add_command(label="更改",command=replace_ip)
    menubar.add_cascade(label="ip地址", menu=editmenu)
    see = Menu(menubar,tearoff=False)
    see.add_command(label="清除焦点",command=clear_focus)
    see.add_command(label="刷新",command=update)
    menubar.add_cascade(label="视图",menu=see)
    about = Menu(menubar,tearoff=False)
    about.add_command(label="设置",command=setting)
    about.add_command(label="关于",command=aboutme)
    about.add_command(label="退出",command=exit)
    menubar.add_cascade(label="帮助",menu=about)
    root.config(menu=menubar)
    '''
    Button(root,text="添加",command=add).grid(row=0,column=2)
    Button(root,text="更改ip地址",command=replace_ip).grid(row=1,column=2)
    Button(root,text="删除",command=delete).grid(row=2,column=2)
    Button(root,text="写入",command=write).grid(row=3,column=2)
    Button(root,text="备份",command=backup).grid(row=4,column=2)
    Button(root,text="恢复",command=recovery).grid(row=5,column=2)
    Button(root,text="清除焦点",command=clear_focus).grid(row=6,column=2)
    Button(root,text="打开hosts",command=open_hosts).grid(row=7,column=2)
    '''
    root.mainloop()