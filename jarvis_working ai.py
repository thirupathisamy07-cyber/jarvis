import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import requests
import pyttsx3
import speech_recognition as sr
import os
import webbrowser
import datetime
import psutil
import platform
import re
from PIL import Image, ImageTk, ImageSequence
from itertools import cycle
OPENROUTER_API_KEY = "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"
MODEL = "openrouter/free"
GIF_PATH = r"C:\Users\Varshini\Desktop\jarvis\jarvis\cyberpunk_bg.gif"
engine = pyttsx3.init()
engine.setProperty('rate', 170)
def speak(text):
    engine.say(text)
    engine.runAndWait()
def speak_async(text):
    threading.Thread(target=speak, args=(text,), daemon=True).start()
def ask_ai(prompt):
    try:
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are JARVIS, a smart AI assistant."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers=headers, json=data, timeout=30)
        result = response.json()
        if "choices" in result and result["choices"]:
            msg = result["choices"][0].get("message")
            if msg and "content" in msg:
                return msg["content"]
        return result.get("error", "AI did not return any response.")
    except Exception as e:
        return f"AI Exception: {e}"
def handle_command(command):
    command = command.lower().strip()
    if command.startswith(("open ", "launch ")):
        name = re.sub(r"open |launch ", "", command)
        url = f"https://www.{name}.com" if "." not in name else f"https://{name}"
        webbrowser.open(url)
        return f"Opening {name}"
    if command.startswith(("search ", "google ")):
        query = re.sub(r"search |google ", "", command)
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching for {query}"
    if command.startswith(("start ", "run ")):
        app = re.sub(r"start |run ", "", command)
        os.system(f"start {app}")
        return f"Launching {app}"
    if command.startswith("create folder "):
        folder = command.replace("create folder ", "")
        os.makedirs(folder, exist_ok=True)
        return f"Folder {folder} created"
    if "time" in command:
        return datetime.datetime.now().strftime("Current time: %H:%M:%S")
    if "date" in command:
        return datetime.datetime.now().strftime("Today is %A, %d %B %Y")
    if "cpu" in command:
        return f"CPU usage: {psutil.cpu_percent()}%"
    if "memory" in command:
        return f"Memory usage: {psutil.virtual_memory().percent}%"
    if "system info" in command:
        return f"{platform.system()} {platform.release()}"
    if "shutdown" in command:
        os.system("shutdown /s /t 5")
        return "System shutting down"
    return ask_ai(command)
root = tk.Tk()
root.title("JARVIS AI Cyberpunk")
root.geometry("800x600")
root.resizable(False, False)
canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
canvas.pack(fill="both", expand=True)
gif = Image.open(GIF_PATH)
frames = [ImageTk.PhotoImage(frame.copy().resize((800,600))) for frame in ImageSequence.Iterator(gif)]
durations = [frame.info.get('duration', 100) for frame in ImageSequence.Iterator(gif)]
frame_cycle = cycle(frames)
bg_item = canvas.create_image(0, 0, anchor="nw", image=next(frame_cycle))

def update_gif(idx=0):
    canvas.itemconfig(bg_item, image=frames[idx])
    root.after(durations[idx], lambda: update_gif((idx+1) % len(frames)))

update_gif()
chat_frame = tk.Toplevel(root)
chat_frame.overrideredirect(True)
chat_frame.attributes("-topmost", True)
chat_frame.attributes("-alpha", 0.6)  
chat_frame.geometry("760x450+20+80")  
def start_move(event):
    chat_frame.x = event.x
    chat_frame.y = event.y

def stop_move(event):
    chat_frame.x = None
    chat_frame.y = None

def do_move(event):
    x = chat_frame.winfo_x() + event.x - chat_frame.x
    y = chat_frame.winfo_y() + event.y - chat_frame.y
    chat_frame.geometry(f"+{x}+{y}")

chat_frame.bind("<Button-1>", start_move)
chat_frame.bind("<ButtonRelease-1>", stop_move)
chat_frame.bind("<B1-Motion>", do_move)

chat_area = ScrolledText(chat_frame, bg="#000000", fg="lime", font=("Consolas", 12),
                         bd=0, highlightthickness=0, insertbackground="white")
chat_area.pack(fill="both", expand=True, padx=5, pady=5)
chat_area.tag_configure("user", foreground="lime")
chat_area.tag_configure("ai", foreground="cyan")
entry = tk.Entry(root, font=("Consolas", 12), bg="#000000", fg="lime", bd=0, insertbackground="white")
entry.place(relx=0.5, rely=0.93, anchor="center", width=600)

send_button = tk.Button(root, text="Send", command=lambda: process_input(entry.get()), bg="#111111", fg="cyan", bd=0)
send_button.place(relx=0.8, rely=0.93, anchor="center", width=80)

voice_button = tk.Button(root, text="🎤 Voice", command=lambda: listen_voice(), bg="#111111", fg="cyan", bd=0)
voice_button.place(relx=0.92, rely=0.93, anchor="center", width=80)
def process_input(user_input):
    user_input = user_input.strip()
    if not user_input:
        return
    chat_area.insert(tk.END, f"You: {user_input}\n", "user")
    chat_area.see(tk.END)
    entry.delete(0, tk.END)
    chat_area.insert(tk.END, "JARVIS: Thinking...\n", "ai")
    chat_area.see(tk.END)

    def worker():
        reply = handle_command(user_input)
        def update_chat():
            chat_area.delete("end-2l", "end-1l") 
            chat_area.insert(tk.END, f"JARVIS: {reply}\n", "ai")
            chat_area.see(tk.END)
            speak_async(reply)
        root.after(0, update_chat)

    threading.Thread(target=worker, daemon=True).start()

entry.bind("<Return>", lambda event: process_input(entry.get()))
def listen_voice():
    def worker():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            chat_area.insert(tk.END, "\nListening...\n", "user")
            chat_area.see(tk.END)
            speak_async("Listening")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            chat_area.insert(tk.END, f"You (Voice): {command}\n", "user")
            chat_area.see(tk.END)
            process_input(command)
        except:
            chat_area.insert(tk.END, "Voice not understood.\n", "ai")
            speak_async("Voice not understood")
    threading.Thread(target=worker, daemon=True).start()
chat_area.insert(tk.END, "JARVIS Online. Awaiting your command...\n", "ai")
entry.focus()
root.mainloop()
