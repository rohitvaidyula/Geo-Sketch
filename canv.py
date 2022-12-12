from tkinter import *
import time
import pandas as pd
from PIL import Image, ImageTk
import random
import os
import numpy as np
import scipy as sp

class MainWindow():
    def __init__(self, root):
        self.root = root
        self.root.title("GeoSketch")
        self.root.geometry("1200x850")
        self.thisStroke = []
        self.strokes = []
        self.points = pd.DataFrame(columns=['x', 'y', 'time'])
        self.canvas = Canvas(self.root, width=1200, height=784, bg="white")
        self.canvas.bind("<Button-1>", self.paint)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.log_stroke)
        self.canvas.pack()
        self.background = Image.open("states/border.png")
        self.img = ImageTk.PhotoImage(self.background)
        self.imgtag = self.canvas.create_image(0, 0, anchor=NW, image=self.img)
        self.undoButton = Button(self.root, text="Undo", command=self.undoCallback)
        self.undoButton.pack(side=LEFT, padx=10, pady=10)
        self.clearButton = Button(self.root, text="Clear", command=self.clearCallback)
        self.clearButton.pack(side=LEFT, padx=10, pady=10)
        self.rollButton = Button(self.root, text="Roll", command=self.rollCallback)
        self.rollButton.pack(side=LEFT, padx=10, pady=10)
        self.submitButton = Button(self.root, text="Submit", command=self.submitCallback)
        self.submitButton.pack(side=LEFT, padx=10, pady=10)
        self.start = 0

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

    def paint(self, event):
        x1, y1 = (event.x - 0.5), (event.y - 0.5)
        x2, y2 = (event.x + 0.5), (event.y + 0.5)
        stroke = self.canvas.create_line(x1, y1, x2, y2, fill="black", width=3)
        self.thisStroke.append(stroke)
        now = int(time.time() * 1000)
        self.points.loc[len(self.points)] = [event.x, event.y, now - self.start]
    
    def log_stroke(self, stroke):
        self.strokes.append(self.thisStroke)
        self.thisStroke = []

    def undoCallback(self):
        print(self.strokes)
        print(self.points)
        if len(self.strokes) > 0:
            for point in self.strokes.pop():
                self.canvas.delete(point)

    def rollCallback(self):
        i = random.randint(0, len(self.states) - 1)
        self.background.paste(Image.open("states/" + self.states[i] + '.png'), (0, 0), Image.open("states/" + self.states[i] + '.png'))
        self.img = ImageTk.PhotoImage(self.background)
        self.canvas.itemconfig(self.imgtag, image=self.img)
        self.start = int(time.time() * 1000)

    def clearCallback(self):
        self.canvas.delete("all")
        self.points.drop(self.points.index, inplace=True)
        print(self.points)

    def submitCallback(self):
        _, scores = self.recognize_gesture(self.points, self.templates)
        print(scores)

        # get index of highest score
        index = scores.index(min(scores))
        stateLabel = Label(self.root, text=self.states[index])
        stateLabel.pack(side=LEFT, padx=10, pady=10)
        # print(self.states[index])

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
            score = self.compute_hausdorff_distance(point_cloud, gesture_template)
            
            # Add the gesture and its score to the list of recognized gestures
            recognized_gestures.append(gesture_template)
            scores.append(score)
            
        # Return the list of recognized gestures and their scores
        return recognized_gestures, scores

    # Define the function for computing the Hausdorff distance between two point clouds
    def compute_hausdorff_distance(self, point_cloud, template):
        # Convert the point cloud and template to numpy arrays
        point_cloud = np.array(point_cloud)
        template = np.array(template)
        
        # Compute the Euclidean distance between each point in the point cloud and each point in the template
        distances = sp.spatial.distance.cdist(point_cloud, template)
        
        # Compute the Hausdorff distance as the maximum of the minimum distances from each point in the point cloud to the template
        hausdorff_distance = np.max(np.min(distances, axis=1))
        
        return hausdorff_distance

root = Tk()
MainWindow(root)
root.mainloop()