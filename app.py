import tkinter as tk
from tkinter import Toplevel, filedialog
from moviepy.editor import VideoFileClip, concatenate_videoclips
import cv2
from PIL import Image, ImageTk

class VideoTaggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Tagger")
        self.video_path = None
        self.segments = []
        self.current_tag = None
        self.start_time = None
        self.playback_speed = 1.0
        self.is_paused = False
        self.cap = None
        
        self.setup_initial_ui()
    
    def setup_initial_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack()

        # Load button
        self.load_button = tk.Button(main_frame, text="Load Video", command=self.load_video, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white")
        self.load_button.pack(pady=10)
        
        # Input field for team name
        self.team_input_label = tk.Label(main_frame, text="Digite o time que você quer gravar no formato 'ATAQUE TIME A':", font=("Arial", 12))
        self.team_input_label.pack(pady=5)
        
        self.team_input_entry = tk.Entry(main_frame, font=("Arial", 12), width=30)
        self.team_input_entry.pack(pady=5)
        
        # Begin button
        self.begin_button = tk.Button(main_frame, text="Begin", command=self.open_video_controls, font=("Arial", 12, "bold"), bg="#e7e7e7", fg="black")
        self.begin_button.pack(pady=20)
    
    def load_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
    
    def open_video_controls(self):
        self.current_tag = self.team_input_entry.get()
        if not self.video_path or not self.current_tag:
            print("Please load a video and enter a team name before beginning.")
            return
        
        self.control_window = Toplevel(self.root)
        self.control_window.title("Video Controls")
        self.control_window.bind("<space>", self.toggle_tag)
        
        # Frame around video for margin and border
        self.video_frame = tk.Frame(self.control_window, padx=20, pady=20, highlightbackground="black", highlightthickness=2)
        self.video_frame.pack(pady=10)
        
        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack()
        
        control_frame = tk.Frame(self.control_window, padx=10, pady=10)
        control_frame.pack()
        
        self.start_button = tk.Button(control_frame, text="START", command=self.start_play, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white")
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.pause_button = tk.Button(control_frame, text="Pause", command=self.pause_video, font=("Arial", 10), bg="#e7e7e7", fg="black")
        self.pause_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.rewind_button = tk.Button(control_frame, text="Rewind 5s", command=self.rewind_video, font=("Arial", 10), bg="#e7e7e7", fg="black")
        self.rewind_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.speed_1x_button = tk.Button(control_frame, text="1x Speed", command=lambda: self.set_playback_speed(1.0), font=("Arial", 10))
        self.speed_1x_button.grid(row=1, column=0, padx=5, pady=5)
        
        self.speed_2x_button = tk.Button(control_frame, text="2x Speed", command=lambda: self.set_playback_speed(2.0), font=("Arial", 10))
        self.speed_2x_button.grid(row=1, column=1, padx=5, pady=5)
        
        self.speed_3x_button = tk.Button(control_frame, text="3x Speed", command=lambda: self.set_playback_speed(3.0), font=("Arial", 10))
        self.speed_3x_button.grid(row=1, column=2, padx=5, pady=5)

        self.speed_4x_button = tk.Button(control_frame, text="4x Speed", command=lambda: self.set_playback_speed(4.0), font=("Arial", 10))
        self.speed_4x_button.grid(row=1, column=3, padx=5, pady=5)
        
        self.start_tag_button = tk.Button(control_frame, text="Start Tag", command=self.start_tag, state=tk.NORMAL, relief=tk.RAISED, font=("Arial", 10), bg="#FFEB3B", fg="black")
        self.start_tag_button.grid(row=2, column=0, padx=5, pady=5)
        
        self.end_tag_button = tk.Button(control_frame, text="End Tag", command=self.end_tag, state=tk.DISABLED, relief=tk.SUNKEN, font=("Arial", 10), bg="#FFEB3B", fg="black")
        self.end_tag_button.grid(row=2, column=1, padx=5, pady=5)
        
        self.save_button = tk.Button(control_frame, text="Save Tagged Video", command=self.save_video, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white")
        self.save_button.grid(row=2, column=2, padx=5, pady=5)
        
        self.progress_frame = tk.Frame(self.control_window, padx=10, pady=10)
        self.progress_frame.pack(fill=tk.X, pady=5)
        
        self.time_label = tk.Label(self.progress_frame, text="00:00:00", font=("Arial", 10))
        self.time_label.pack(side=tk.LEFT, padx=10)
        
        self.progress_bar = tk.Scale(self.progress_frame, from_=0, to=100, orient=tk.HORIZONTAL, showvalue=0, length=400)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.remaining_label = tk.Label(self.progress_frame, text="00:00:00", font=("Arial", 10))
        self.remaining_label.pack(side=tk.RIGHT, padx=10)
    
    def update_progress(self):
        if self.cap is not None and self.cap.isOpened():
            current_pos = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            total_duration = self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.cap.get(cv2.CAP_PROP_FPS)
            
            self.progress_bar.set((current_pos / total_duration) * 100)
            self.time_label.config(text=self.format_time(current_pos))
            self.remaining_label.config(text=self.format_time(total_duration - current_pos))
            
            if not self.is_paused:
                self.control_window.after(500, self.update_progress)
    
    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        return f"{int(hours):02}:{int(mins):02}:{int(secs):02}"
    
    def toggle_tag(self, event=None):
        if self.start_tag_button['state'] == tk.NORMAL:
            self.start_tag()
        elif self.end_tag_button['state'] == tk.NORMAL:
            self.end_tag()
    
    def play_video(self):
        if not self.is_paused:
            ret, frame = self.cap.read()
            if ret:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
                delay = int(1000 / (self.cap.get(cv2.CAP_PROP_FPS) * self.playback_speed))
                self.video_label.after(delay, self.play_video)
            else:
                self.cap.release()
    
    def start_play(self):
        if self.video_path:
            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.video_path)
            self.is_paused = False
            self.play_video()
            self.update_progress()
    
    def pause_video(self):
        self.is_paused = True
    
    def rewind_video(self):
        if self.cap is not None and self.cap.isOpened():
            current_pos = self.cap.get(cv2.CAP_PROP_POS_MSEC)
            new_pos = max(current_pos - 5000, 0)  # Rewind 5 seconds
            self.cap.set(cv2.CAP_PROP_POS_MSEC, new_pos)
    
    def set_playback_speed(self, speed):
        self.playback_speed = speed
        if self.cap is not None and self.cap.isOpened():
            self.is_paused = True
            self.is_paused = False
            self.play_video()
    
    def start_tag(self):
        if self.cap is not None and self.cap.isOpened():
            self.start_time = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            print(f"Tag started at {self.start_time:.2f} seconds")
            self.start_tag_button.config(state=tk.DISABLED, relief=tk.SUNKEN)
            self.end_tag_button.config(state=tk.NORMAL, relief=tk.RAISED)
            self.video_frame.config(highlightbackground="red")
    
    def end_tag(self):
        if self.cap is not None and self.cap.isOpened() and self.start_time is not None:
            end_time = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            self.segments.append((self.start_time, end_time, self.current_tag))
            print(f"Tagged {self.current_tag} from {self.start_time:.2f} to {end_time:.2f} seconds")
            self.start_time = None
            self.start_tag_button.config(state=tk.NORMAL, relief=tk.RAISED)
            self.end_tag_button.config(state=tk.DISABLED, relief=tk.SUNKEN)
            self.video_frame.config(highlightbackground="black")
    
    def save_video(self):
        if not self.segments or not self.video_path:
            return
        
        clip = VideoFileClip(self.video_path)
        tagged_clips = []
        
        for segment in self.segments:
            start_time, end_time, tag_type = segment
            subclip = clip.subclip(start_time, end_time)
            tagged_clips.append(subclip)
        
        final_clip = concatenate_videoclips(tagged_clips)
        final_clip.write_videofile(f"{self.current_tag}.mp4", codec="libx264")
        print(f"Tagged video saved as '{self.current_tag}.mp4'")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoTaggerApp(root)
    root.mainloop()
