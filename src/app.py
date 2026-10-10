"""Local desktop application: file selection, ROI, two tasks, auditable export."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from PIL import Image,ImageTk
import threading,queue
from predict import run
from flower_predict import run as flower_run
R=Path(__file__).resolve().parents[1]
class App:
 def __init__(self,root):
  self.root=root;root.title('葡萄疏果识别 · 课程设计');root.geometry('1120x820');self.path=None;self.roi=None;self.scale=1;self.results=queue.Queue()
  top=ttk.Frame(root,padding=12);top.pack(fill='x');ttk.Label(top,text='葡萄疏果识别与可见果粒计数',font=('',18,'bold')).pack(anchor='w');ttk.Label(top,text='先打开照片，再拖框选择一穗。绿色为保留，红色为建议去除；结果需要人工复核。').pack(anchor='w',pady=6)
  controls=ttk.Frame(root,padding=10);controls.pack(fill='x');ttk.Button(controls,text='打开照片',command=self.open).pack(side='left',padx=4)
  self.task=tk.StringVar(value='果粒（辅助模型）');ttk.Combobox(controls,textvariable=self.task,state='readonly',values=['果粒（辅助模型）','幼果（试验模型）','花序 / 小穗'],width=20).pack(side='left',padx=4)
  self.conf=tk.StringVar(value='0.30');self.ratio=tk.StringVar(value='0.70');self.target=tk.StringVar(value='')
  for name,var in [('置信度',self.conf),('小果比例',self.ratio),('可见保留上限',self.target)]:
   ttk.Label(controls,text=name).pack(side='left',padx=4);ttk.Entry(controls,textvariable=var,width=6).pack(side='left')
  self.go=ttk.Button(controls,text='识别并导出',command=self.start);self.go.pack(side='left',padx=8)
  self.canvas=tk.Canvas(root,width=1080,height=610,bg='#edf1ee',highlightthickness=0);self.canvas.pack(fill='both',expand=True,padx=12);self.canvas.bind('<ButtonPress-1>',self.down);self.canvas.bind('<B1-Motion>',self.drag);self.canvas.bind('<ButtonRelease-1>',self.up)
  self.status=tk.StringVar(value='等待图像。保留上限留空时，仅按相对大小筛选；不推算遮挡果粒。');ttk.Label(root,textvariable=self.status,padding=12,wraplength=1080).pack(fill='x');root.after(100,self.poll)
 def display(self,path):
  im=Image.open(path).convert('RGB');self.original_size=im.size;self.scale=min(1080/im.width,610/im.height,1);im=im.resize((round(im.width*self.scale),round(im.height*self.scale)));self.photo=ImageTk.PhotoImage(im);self.canvas.delete('all');self.canvas.create_image(0,0,anchor='nw',image=self.photo)
 def open(self):
  p=filedialog.askopenfilename(filetypes=[('Images','*.jpg *.jpeg *.png *.bmp'),('All','*.*')])
  if p:self.load(p)
 def load(self,p):
  self.path=Path(p);self.roi=None;self.display(p);self.status.set('已打开 '+self.path.name+'；可拖框选择单穗。')
 def down(self,e):
  if not self.path:return
  self.anchor=(e.x,e.y);self.canvas.delete('roi');self.canvas.create_rectangle(e.x,e.y,e.x,e.y,outline='#ed9b00',width=3,tags='roi')
 def drag(self,e):
  if hasattr(self,'anchor'):self.canvas.coords('roi',*self.anchor,e.x,e.y)
 def up(self,e):
  if not hasattr(self,'anchor'):return
  x,y=self.anchor;w,h=self.original_size;b=[max(0,min(w,int(min(x,e.x)/self.scale))),max(0,min(h,int(min(y,e.y)/self.scale))),max(0,min(w,int(max(x,e.x)/self.scale))),max(0,min(h,int(max(y,e.y)/self.scale)))]
  self.roi=b if b[2]-b[0]>4 and b[3]-b[1]>4 else None;self.status.set('选定ROI：'+str(self.roi))
 def start(self):
  if self.path is None:messagebox.showinfo('提示','请先打开图像');return
  try:
   conf=float(self.conf.get());ratio=float(self.ratio.get());target=int(self.target.get()) if self.target.get().strip() else None
   if not 0<conf<1 or not 0<ratio<=1 or (target is not None and target<0):raise ValueError()
  except ValueError:messagebox.showerror('参数错误','置信度须在0与1之间；比例须在0与1之间；保留上限须为非负整数或空白。');return
  task=self.task.get();kind='flower' if task=='花序 / 小穗' else 'young' if task.startswith('幼果') else 'berry_aux';weights=R/'runs'/kind/'weights/best.pt'
  if not weights.exists():messagebox.showerror('缺少模型','请解压交付包中的 runs 模型文件夹');return
  image_path=self.path;roi=self.roi
  out=R/'outputs'/f'{image_path.stem}_{kind}';self.go.state(['disabled']);self.status.set('正在识别，请稍候……')
  def work():
   try:self.results.put((True,flower_run(image_path,weights,out,conf) if kind=='flower' else run(image_path,weights,out,ratio,target,conf,roi),out))
   except Exception as e:self.results.put((False,str(e),out))
  threading.Thread(target=work,daemon=True).start()
 def poll(self):
  try:
   ok,r,out=self.results.get_nowait();self.go.state(['!disabled'])
   if ok:
    self.display(out/'annotated.jpg');self.status.set((f"可见 {r['visible_count']} 粒；建议去除 {r['remove_count']}；保留 {r['keep_count']}。" if 'visible_count' in r else str(r['counts']))+' 已导出至 '+str(out))
   else:self.status.set('运行失败：'+r)
  except queue.Empty:pass
  self.root.after(100,self.poll)
if __name__=='__main__':
 root=tk.Tk();App(root);root.mainloop()
