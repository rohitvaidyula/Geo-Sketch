from tkinter import *
from tkinter import messagebox
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
        # add dropdown menu for selecting mode: states or rivers
        self.mode = StringVar(self.root)
        self.mode.set("Select Mode")
        self.modeMenu = OptionMenu(self.root, self.mode, "States", "Rivers")
        self.undoStrokeButton = Button(self.root, text="Undo Stroke", command=self.undoStrokeCallback)
        self.undoSubmitButton = Button(self.root, text="Undo Submit", command=self.undoSubmitCallback)
        self.submitButton = Button(self.root, text="Submit", command=self.submitCallback)
        self.averageLabel = Label(self.root, text="Average: ")
        self.start = 0
        self.strokeCount = 1

        # place widgets in grid
        self.canvas.grid(row=0, column=0, columnspan=24, rowspan=16)
        self.gradesDisplay.grid(row=0, column=24, columnspan=2, rowspan=16)
        self.modeMenu.grid(row=16, column=0)
        self.undoStrokeButton.grid(row=16, column=1)
        self.undoSubmitButton.grid(row=16, column=2)
        self.submitButton.grid(row=16, column=23)
        self.averageLabel.grid(row=16, column=24)

        self.states = ['alabama', 'alaska', 'arizona', 'arkansas', 'california', 
                       'colorado', 'connecticut', 'delaware', 'florida', 
                       'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 
                       'iowa', 'kansas', 'kentucky', 'louisianna', 'maine', 
                       'maryland', 'massachusetts', 'michigan', 'minnesota', 'mississippi', 
                       'missouri', 'montana', 'nebraska', 'nevada', 'new_hampshire', 
                       'new_jersey', 'new_mexico', 'new_york', 'north_carolina', 'north_dakota', 
                       'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode_island', 
                       'south_carolina', 'south_dakota', 'tennessee', 'texas', 'utah', 
                       'vermont', 'virginia', 'washington', 'westvirginia', 'wisconsin', 'wyoming']

        self.rivers = ['alabama_river', 'arkansas_river', 'brazos_river', 'canadian_river', 'chattahoochee_river', 
                       'colorado_river', 'columbia_river', 'connecticut_river', 'delaware_river', 'gila_river',
                       'green_river', 'hudson_river', 'illinois_river', 'mississippi_river', 'missouri_river', 
                       'ohio_river', 'pecos_river', 'platte_river', 'potomac_river', 'red_river', 
                       'red_river_(North)', 'rio_grande_river', 'sacramento_river', 'san_joquin_river', 'savannah_river', 
                       'snake_river', 'susquehanna_river', 'tennessee_river', 'wabash_river']

        # go through templates folder and store csvs in list of dataframes
        self.state_templates = []
        for file in os.listdir("state_templates"):
            if file == 'border.csv': continue
            if file.endswith(".csv"):
                self.state_templates.append(pd.read_csv("state_templates/" + file))

        self.river_templates = []
        for file in os.listdir('river_templates'):
            if file.endswith('.csv'):
                self.river_templates.append(pd.read_csv('river_templates/' + file))

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

    def undoSubmitCallback(self):
        # peek at image history and display with PIL.show
        self.statesSubmitted.pop()
        self.gradesDisplay.delete(END)
        self.background = Image.open("states/border.png")
        self.img = ImageTk.PhotoImage(self.background)
        for state in self.statesSubmitted:
            if 'river' in state:
                self.background.paste(Image.open("rivers/" + state + '.png'), (0, 0), Image.open("rivers/" + state + '.png'))
            else:
                self.background.paste(Image.open("states/" + state + '.png'), (0, 0), Image.open("states/" + state + '.png'))
            self.img = ImageTk.PhotoImage(self.background)
        self.canvas.itemconfig(self.imgtag, image=self.img)
        self.grades.pop()
        self.updateAverage()

    def submitCallback(self):
        if len(self.points) == 0:
            return
        # if mode is 'Select Mode' then alert user to select mode
        if self.mode.get() == 'Select Mode':
            messagebox.showwarning("Mode Error", "Please select a mode")
            return
        elif self.mode.get() == 'States':
            _, scores = self.recognize_gesture(self.points, self.state_templates)
        else:
            _, scores = self.recognize_gesture(self.points, self.river_templates)
        # print(scores)

        # get index of highest score
        index = scores.index(min(scores))
        grade = min((100-2*scores[index]), (100-20*math.log(scores[index])))

        # ternary operators to make sure grade is between 0 and 100
        grade = grade if grade < 100 else 100
        grade = grade if grade > 0 else 0

        if self.mode.get() == 'Rivers':
            grade = (grade ** 0.5) * 10
        print("Grade: " + str(grade))
        print("Score: " + str(scores[index]))

        if self.mode.get() == 'States':
            self.place_template(Image.open("states/" + self.states[index] + '.png'))
            self.statesSubmitted.append(self.states[index])
            # insert state and grade into grades list with capitalization on first letter, and grade rounded to 2 decimal places
            # split states[index] by _ and capitalize each word
            self.gradesDisplay.insert(END, ' '.join([word.capitalize() for word in self.states[index].split('_')]) + ": " + str(round(grade, 2)))
            # self.gradesDisplay.insert(END, self.states[index].capitalize() + ": " + str(round(grade, 2)))
        else:
            self.place_template(Image.open("rivers/" + self.rivers[index] + '.png'))
            self.statesSubmitted.append(self.rivers[index])
            # insert state and grade into grades list with capitalization on first letter, and grade rounded to 2 decimal places
            # split rivers[index] by _ and capitalize each word
            self.gradesDisplay.insert(END, ' '.join([word.capitalize() for word in self.rivers[index].split('_')]) + ": " + str(round(grade, 2)))
            # self.gradesDisplay.insert(END, self.rivers[index].capitalize() + ": " + str(round(grade, 2)))
        
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
        if self.mode.get() == 'States':
            self.background.paste(template, (0, 0), template)
        else:
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

root = Tk()
MainWindow(root)
root.mainloop()