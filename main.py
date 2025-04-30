import subprocess
import tkinter
from tkinter import *
from tkinter import ttk
import time
import playsound
from playsound import playsound
import threading
import os

# Ask for player's name and age
player_name = input("Enter your name: ")
age = input("Enter your age: ")

if int(age) >= 18:
    root = Tk()
    root.title("SQUID GAME")
    root.geometry("1530x1080")

    def play():
        time.sleep(8)
        playsound(r"D:\Squid-Game-main\Squid-Game-main\Squid-Game-main (1)\Squid-Game-main\instructions.mp3")
        time.sleep(2)
        subprocess.run(["python", r"D:\Squid-Game-main\Squid-Game-main\Squid-Game-main (1)\Squid-Game-main\redlightgreen.py", player_name])  # Passing name

    # Button to start playing instructions
    play_button = Button(root, text="PLAYING INSTRUCTIONS IN 10 SECS", font=("Helvetica", 32),
                         relief=GROOVE, command=lambda: threading.Thread(target=play).start())
    play_button.pack(pady=20)

    # Information Label
    Label(root, text="PLEASE LISTEN TO THE INSTRUCTIONS CAREFULLY BEFORE PRESSING THE START BUTTON",
          font=("times new roman", 10, "bold")).pack(pady=20)

    # Background Image
    bg = PhotoImage(file=r"D:\Squid-Game-main\Squid-Game-main\Squid-Game-main (1)\Squid-Game-main\squid6.png")
    canvas1 = Canvas(root, width=1530, height=1080)
    canvas1.pack(fill="both", expand=True)
    canvas1.create_image(0, 0, image=bg, anchor="nw")

    # Game Title
    w2 = Label(root, justify=LEFT, text="Squid Game - 1", font=("times", 34))
    w2.place(x=50, y=50)

    w3 = Label(root, justify=LEFT, text="A Real Life\nDepiction", font=("times", 34))
    w3.place(x=1190, y=30)

    # Function to start the game
    def start_game():
        subprocess.call(["python", r"D:\Squid-Game-main\Squid-Game-main\Squid-Game-main (1)\Squid-Game-main\redlightgreen.py", player_name])  # Passing name

    # New Window for Start Button
    start_window = tkinter.Toplevel()

    img2 = PhotoImage(file=r"D:\Squid-Game-main\Squid-Game-main\Squid-Game-main (1)\Squid-Game-main\Frame.png")
    btnStart = Button(start_window, image=img2, relief=FLAT, border=0, command=start_game)
    btnStart.pack()

    root.mainloop()

else:
    print("You are not eligible to play.")