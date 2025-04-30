from playsound import playsound
from tkinter import*
import os
import cv2
 
root = Tk()
root.geometry("500x400")
 
# making function
def play():
    os.system(r"D:\Squid-Game-main\Squid-Game-main\Squid-Game-main (1)\Squid-Game-main\redlightgreen.py")
    cv2.waitKey(0)

    
 

 
# making a button which trigger the function so sound can be playeed
play_button = Button(root, text="Play Song", font=("Helvetica", 32),
                     relief=GROOVE, command=play)
play_button.pack(pady=20)
 
info=Label(root,text="Click on the button above to play song ",
           font=("times new roman",10,"bold")).pack(pady=20)
root.mainloop()
