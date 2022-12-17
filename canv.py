from tkinter import *
import time
import pandas as pd
from PIL import Image, ImageTk
import random
import os
import numpy as np
import scipy as sp
import math

class MainWindow():
    def __init__(self, root):
        self.root = root
        self.root.title("GeoSketch")
        self.root.geometry("1360x835")
        self.thisStroke = []
        self.strokes = []
        self.statesSubmitted = []
        self.grades = []
        self.points = pd.DataFrame(columns=['stroke', 'x', 'y', 'time'])
        self.canvas = Canvas(self.root, width=1200, height=800, bg="white")
        self.canvas.bind("<Button-1>", self.paint)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.log_stroke)
        self.background = Image.open("states/border.png")
        self.img = ImageTk.PhotoImage(self.background)
        self.imgtag = self.canvas.create_image(0, 0, anchor=NW, image=self.img)
        self.gradesDisplay = Listbox(self.root, width=25, height=50)
        self.undoStateButton = Button(self.root, text="Undo State", command=self.undoStateCallback)
        self.undoStrokeButton = Button(self.root, text="Undo Stroke", command=self.undoStrokeCallback)
        self.submitButton = Button(self.root, text="Submit", command=self.submitCallback)
        self.averageLabel = Label(self.root, text="Average: ")
        self.start = 0
        self.strokeCount = 1

        # place widgets in grid
        self.canvas.grid(row=0, column=0, columnspan=24, rowspan=16)
        self.gradesDisplay.grid(row=0, column=24, columnspan=2, rowspan=16)
        self.undoStateButton.grid(row=16, column=0)
        self.undoStrokeButton.grid(row=16, column=1)
        self.submitButton.grid(row=16, column=2)
        self.averageLabel.grid(row=16, column=24)

        self.states = ['alabama', 'alaska', 'arizona', 'arkansas', 'california',
          'colorado', 'connecticut', 'delaware', 'florida',
          'georgia', 'hawaii', 'idaho', 'illinois', 'indiana',
          'iowa', 'kansas', 'kentucky', 'louisianna', 'maine',
          'maryland', 'massachusetts', 'michigan', 'minnesota', 'mississippi',
          'missouri', 'montana', 'nebraska', 'nevada', 'newhampshire',
          'newjersey', 'newmexico', 'newyork', 'northcarolina', 'northdakota',
          'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhodeisland',
          'southcarolina', 'southdakota', 'tennessee', 'texas', 'utah',
          'vermont', 'virginia', 'washington', 'westvirginia', 'wisconsin', 'wyoming']

        # go through templates folder and store csvs in list of dataframes
        self.templates = []
        for file in os.listdir("templates"):
            if file == 'border.csv': continue
            if file.endswith(".csv"):
                self.templates.append(pd.read_csv("templates/" + file))

    def updateAverage(self):
        if len(self.grades) == 0:
            self.averageLabel.config(text="Average: ")
            return
        avg = np.average(self.grades)
        self.averageLabel.config(text="Average: " + str(round(avg, 2)))


    def paint(self, event):
        x1, y1 = (event.x - 0.5), (event.y - 0.5)
        x2, y2 = (event.x + 0.5), (event.y + 0.5)
        stroke = self.canvas.create_line(x1, y1, x2, y2, fill="black", width=3)
        self.thisStroke.append(stroke)
        now = int(time.time() * 1000)
        self.points.loc[len(self.points)] = [self.strokeCount, event.x, event.y, now - self.start]

    def log_stroke(self, stroke):
        self.strokeCount += 1
        self.strokes.append(self.thisStroke)
        self.thisStroke = []

    def undoStrokeCallback(self):
        # remove last stroke from points by stroke number
        self.points.drop(self.points[self.points['stroke'] == self.strokeCount - 1].index, inplace=True)
        if len(self.strokes) > 0:
            for point in self.strokes.pop():
                self.canvas.delete(point)
            self.strokeCount -= 1
        print(self.strokes)
        print(self.points)

    def undoStateCallback(self):
        # peek at image history and display with PIL.show
        self.statesSubmitted.pop()
        self.gradesDisplay.delete(END)
        self.background = Image.open("states/border.png")
        self.img = ImageTk.PhotoImage(self.background)
        for state in self.statesSubmitted:
            self.background.paste(Image.open("states/" + state + '.png'), (0, 0), Image.open("states/" + state + '.png'))
            self.img = ImageTk.PhotoImage(self.background)
        self.canvas.itemconfig(self.imgtag, image=self.img)
        self.grades.pop()
        self.updateAverage()

    def submitCallback(self):
        if len(self.points) == 0:
            return
        _, scores = self.recognize_gesture(self.points, self.templates)
        # print(scores)

        # get index of highest score
        index = scores.index(min(scores))
        if scores[index] < 2:
            grade = 100 - (10 * math.log(scores[index]))
        elif scores[index] < 5:
            grade = 100 - (12 * math.log(scores[index]))
        elif scores[index] < 10:
            grade = 100 - (15 * math.log(scores[index]))
        elif scores[index] < 20:
            grade = 100 - (20 * math.log(scores[index]))
        elif scores[index] < 50:
            grade = 100 - (30 * math.log(scores[index]))
        else:
            grade = 100 - (50 * math.log(scores[index]))

        # ternary operators to make sure grade is between 0 and 100
        grade = grade if grade < 100 else 100
        grade = grade if grade > 0 else 0
        print("Grade: " + str(grade))
        print("Score: " + str(scores[index]))
        self.place_template(Image.open("states/" + self.states[index] + '.png'))
        self.statesSubmitted.append(self.states[index])
        # insert state and grade into grades list with capitalization on first letter, and grade rounded to 2 decimal places
        self.gradesDisplay.insert(END, self.states[index].capitalize() + ": " + str(round(grade, 2)))
        self.grades.append(grade)
        self.updateAverage()

    # Define the function for clearing the strokes list and pasting an input image on the canvas
    def place_template(self, template):
        # Pop each stroke from the strokes list and drop each point in stroke from the canvas
        while len(self.strokes) > 0:
            for point in self.strokes.pop():
                self.canvas.delete(point)

        # Drop all points from the points dataframe
        self.points.drop(self.points.index, inplace=True)

        # Paste the input template on the canvas
        self.background.paste(template, (0, 0), template)
        self.img = ImageTk.PhotoImage(self.background)
        self.canvas.itemconfig(self.imgtag, image=self.img)

    # Define the function for gesture recognition
    def recognize_gesture(self, point_cloud, gesture_templates):
        # Convert the point cloud and gesture templates to numpy arrays
        point_cloud = point_cloud[['x', 'y']].to_numpy()
        gesture_templates = [template[['x', 'y']].to_numpy() for template in gesture_templates]

        # Initialize the list of recognized gestures and their scores
        recognized_gestures = []
        scores = []

        # Iterate through each gesture template
        for gesture_template in gesture_templates:
            # Compute the similarity between the point cloud and the gesture template using some similarity measure (e.g. Hausdorff distance)
            score = self.compute_distance(point_cloud, gesture_template)

            # Add the gesture and its score to the list of recognized gestures
            recognized_gestures.append(gesture_template)
            scores.append(score)

        # Return the list of recognized gestures and their scores
        return recognized_gestures, scores

    # Define the function for computing the Hausdorff distance between two point clouds
    def compute_distance(self, point_cloud, template):
        # Convert the point cloud and template to numpy arrays
        point_cloud = np.array(point_cloud)
        template = np.array(template)

        # Compute the Euclidean distance between each point in the point cloud and each point in the template
        distances = sp.spatial.distance.cdist(point_cloud, template)

        # Compute the Hausdorff distance as the maximum of the minimum distances from each point in the point cloud to the template
        hausdorff_distance = np.average(np.min(distances, axis=0))

        return hausdorff_distance


starter_window = Tk()
def main_paper():
    starter_window.destroy()
    root = Tk()
    MainWindow(root)
    root.mainloop()
def practice_mode():
    p_mode = Toplevel(starter_window)
    p_mode.title("Practice Mode")
    p_mode.geometry("1200x784")
    C = Canvas(p_mode, bg="white", height=784, width=1200)
    p_image = PhotoImage(file = "C:/Users/vaidy/OneDrive/Desktop/Geo-Sketch/practice.png")
    C.create_image(0, 0, anchor = NW, image = p_image)
    C.pack(fill=BOTH, expand=1)

    def x_and_y(event):
        global prev
        prev = event
    def draw(event):
        global prev
        C.create_line(prev.x, prev.y, event.x, event.y, fill="black", width=5)
        prev = event
    C.bind("<Button-1>", x_and_y)
    C.bind("<B1-Motion>", draw)
    p_mode.mainloop()

starter_window.title("Geo-Sketch")
starter_window.geometry("1200x800")
starter_window.overrideredirect
window_label = Label(starter_window, text= "Welcome to GEO-SKETCH!", font=('Comic Sans MS', 30)).pack(pady=20)
small_label = Label(starter_window, text= "Choose one of the options below!", font=('Comic Sans MS', 16)).pack(pady=20)
free_draw = Button(starter_window, text = "Free Draw Mode", command=main_paper)
practice = Button(starter_window, text = "Practice Mode", command=practice_mode)
practice.pack(side=TOP)
free_draw.pack(side=TOP)
starter_window.mainloop()