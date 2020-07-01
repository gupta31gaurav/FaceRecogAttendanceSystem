from tkinter import *
from tkinter import ttk, filedialog, messagebox
import tkinter.font as font
import psycopg2
import cv2
import numpy as np
from PIL import Image


#for basic window
root=Tk()
root.title('Attendance System')
root.geometry("800x500")
root.resizable(0,0) #for setting a fixed size
root.configure(bg='lightgray')
filepath="" #for storing the path of the uploaded image
conn=psycopg2.connect(host='localhost', database='my_first_db', user='postgres', password='postgres')
curr= conn.cursor()
#creating cascade
cascadePath ="haarcascade_frontalface_default.xml"
faceCascade =cv2.CascadeClassifier(cascadePath);
#recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainedd.xml")
attendance_data =[]

#for creating menubar with tabs
menu=Menu(root)
root.config(menu=menu)
aboutmenu=Menu(menu)
menu.add_cascade(label='About',menu=aboutmenu)
aboutmenu.add_command(label='About the application')
contactmenu=Menu(menu)
menu.add_cascade(label='Contact',menu=contactmenu)
contactmenu.add_command(label='Contact creator')


#adding logo image
mvnlogo=PhotoImage(file='mvnlogo.png')
logolabel=Label(root,image=mvnlogo)
logolabel.place(x=200,y=20)
logolabel.pack()


#functions: Frame/Window handling
def checkattend():
    toolbar.pack_forget()
    logolabel.pack_forget()
    #loginlabel.pack()
    checkattendance.pack()

def home():
    userentry.delete('0','end')
    passentry.delete('0','end')
    listbox.delete(0,END)
    attendance_data.clear()
    checkattendance.pack_forget()
    resultwala.pack_forget()
    logolabel.pack()
    toolbar.pack(side="bottom", fill="x", padx=100, pady=80)

def attendanceshow():
    userentry.delete('0', 'end')
    passentry.delete('0', 'end')
    checkattendance.pack_forget()
    resultwala.pack()

def update_listbox(*args):
  search_term = search_var.get()
  listbox.delete(0, END)
  for item in attendance_data:
    if search_term.lower() in item.lower():
      listbox.insert(END, item)

#functions: Image processing
def UploadAction(event=None):
    global filepath
    filepath = filedialog.askopenfilename(initialdir="C:/Users/GAURAV/Desktop/",title="Select Image")
    labels=imgprocess()
    print(labels)
    updateattendance(labels)
    print('Selected Image:', filepath)

def imgprocess(event=None):
    global filepath
    image_path=filepath
    predict_image_pil = Image.open(image_path).convert('L')
    predict_image = np.array(predict_image_pil, 'uint8')
    faces = faceCascade.detectMultiScale(predict_image)
    labels=[]
    for (x, y, w, h) in faces:
        nbr_predicted, conf = recognizer.predict(predict_image[y: y + h, x: x + w])
        if (conf<=100):
            labels.append(nbr_predicted)
            cv2.imshow("recognised", predict_image[y: y + h, x: x + w])
            cv2.waitKey(1000)
        elif (conf > 100):
            print("Some faces are not recognised")
            cv2.imshow("Imposter",predict_image[y: y+h, x: x+w])
            cv2.waitKey(1000)
    cv2.destroyAllWindows()
    return labels

#functions: Database Handling
def wronglogin():
    messagebox.showerror("Login Denied","Sorry, the login you entered is incorrect.")

def login():
    #global username, userpass
    username = userentry.get()
    userpass = passentry.get()
    tuplee = (username, userpass)
    loginquery = "select EXISTS(select * from teachers where t_name= %s AND pass= %s)"
    curr.execute(loginquery, tuplee)
    if curr.fetchone()[0] == 1:
        {
            fetchattendance()  # print('Table exists')
        }
    else:
        wronglogin()

def updateattendance(labels):
    updatequery='update students set totalcount= totalcount + 1 where rno= %s'
    for label in labels:
        tuplee=(label,)
        curr.execute(updatequery,tuplee)
    conn.commit()

def fetchattendance():
    global attendance_data, result
    userentry.delete('0','end')
    passentry.delete('0','end')
    checkattendance.pack_forget()
    resultwala.pack()
    curr.execute("select * from students order by rno")
    result = curr.fetchall()
    for x in result:
        str="Roll No. {} Name: {} Attendance {} ".format(x[0],x[1],x[2])
        listbox.insert(END,str)
        attendance_data.append(str)

#frame name is toolbar for home page
toolbar = Frame(root,bg='lightgray')
toolbar.pack(side="bottom", fill="x", padx=100, pady=80)
myfont=font.Font(size=20,family='Comic Sans MS')
myfont1=font.Font(size=10,family='Comic Sans MS')
button1 = Button(toolbar, text="Check Attendance",bg='gray' ,height=5,width=15, command=checkattend)
button2 = Button(toolbar, text="Upload Picture",bg='gray',height=5,width=15, command=UploadAction)
button1['font']=myfont
button2['font']=myfont
sep = ttk.Separator(toolbar) #creating button seperator

button1.pack(side="left")
sep.pack(side="left", fill="y", padx=40, pady=40)
button2.pack(side="left")



#frame name checkattendance for login
checkattendance=Frame(root,bg='lightgray')
checkattendance.pack()#side="bottom",fill="x",padx=100,pady=100
loginlogo=PhotoImage(file='loginlogo.PNG')
loginlabel=Label(checkattendance,image=loginlogo, padx=100, pady=50)
loginlabel.place(x=200,y=20)
loginlabel.pack()
userlabel=Label(checkattendance,text='Username :').pack(pady=5)
userentry=Entry(checkattendance, justify='center')
userentry.pack(pady=5)
passlabel=Label(checkattendance,text='Password :').pack(pady=5)
passentry=Entry(checkattendance, show="X", justify='center')
passentry.pack(pady=5)
loginbutton=Button(checkattendance,text="Login",bg='gray',height=3,width=10, command=login)
homebutton=Button(checkattendance,text='Home',bg='gray',height=3,width=10, command=home)
loginbutton['font']=myfont1
homebutton['font']=myfont1
loginbutton.pack(side='left',padx=50,pady=10)
homebutton.pack(side='right',padx=50,pady=10)
checkattendance.pack_forget()



#frame name resultwala for attendance result
resultwala=Frame(root,bg='lightgray',width=700,height=400)
resultwala.pack()
sf= font.Font(family='comic sans MS', weight='bold')
search_var = StringVar()
search_var.trace('w', update_listbox)
searchlabel= Label(resultwala,text='Search', font=sf)
searchlabel.pack()
searchbox = Entry(resultwala, textvariable=search_var, font=sf)
searchbox.pack()
homebutton=Button(resultwala,text='Home',bg='gray',height=2,width=10, command=home)
homebutton.pack()
scroll= Scrollbar(resultwala)
scroll.pack(side=RIGHT, fill= Y)
listbox=Listbox(resultwala, height=400, width=400 , font=sf)
listbox.pack(fill=BOTH, expand= NO)
listbox.config(yscrollcommand=scroll.set)
scroll.config(command=listbox.yview)
resultwala.pack_forget()

mainloop()
