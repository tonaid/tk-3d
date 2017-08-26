from Tkinter import *
import numpy as np
import math


class Segment():
    def __init__(self, matrix=np.matrix([]), color=''):
        self.matrix = matrix
        self.color = color

    def to_vectors(self):
        for i in range(len(self.matrix[0,:].tolist()[0])):
            yield self.matrix[:,i]

class Eye():
    def __init__(self, location=np.array([0,0,69])):
        self.location = location
        self.scale = 100
        self.canv_center = [960, 840]
        self.theta = 0

    def render(self, segments=[]):
        for seg in segments:
            coords = []
            for vector in seg.to_vectors():
                try:
                    coord = self.rotate(vector)
                    xp = ((coord[0] - self.location.tolist()[0]) / -(coord[1] - self.location.tolist()[1])) * self.scale
                    yp = ((coord[2] - self.location.tolist()[2]) / -(coord[1] - self.location.tolist()[1])) * self.scale
                    coords += [self.canv_center[0] + xp, self.canv_center[1] + yp]
                except(ZeroDivisionError):
                    pass

            yield {'coords':coords, 'color':seg.color}

    def rotate(self, vector):
        self.theta = math.radians(self.theta)
        rotation = np.matrix([[math.cos(self.theta),math.sin(self.theta),0],[-math.sin(self.theta),math.cos(self.theta),0],[0,0,1]])
        self.theta = math.degrees(self.theta)
        return np.dot(rotation,vector).ravel().tolist()[0]


    def move_left(self):
        self.location[0] += 30

    def move_right(self):
        self.location[0] -= 30

    def move_forward(self):
        self.location[1] += 30

    def move_back(self):
        self.location[1] -= 30

    def rotate_left(self):
        self.theta += 1

    def rotate_right(self):
        self.theta -= 1


class Engine():
    def __init__(self):
        self.update_delay =  10 #milliseconds
        self.root = Tk()
        self.root.attributes('-fullscreen', True)
        self.root.config(bg='black', highlightbackground='black')
        self.canvas = Canvas(self.root, height=1080, width=1920, bg='#2f343f', highlightbackground='#2f343f')
        self.canvas.pack()
        self.eye = Eye()
        self.segments = []

        self.root.bind('w', self.move_forward)
        self.root.bind('a', self.move_left)
        self.root.bind('s', self.move_back)
        self.root.bind('d', self.move_right)
        self.root.bind('q', self.rotate_left)
        self.root.bind('e', self.rotate_right)

    def update(self):
        self.canvas.delete('all')
        for polygon in self.eye.render(self.segments):
            self.canvas.create_polygon(polygon['coords'], outline='black', fill=polygon['color'])

        self.root.after(self.update_delay, self.update)

    def move_left(self, event):
        self.eye.move_left()

    def move_right(self, event):
        self.eye.move_right()

    def move_forward(self, event):
        self.eye.move_forward()

    def move_back(self, event):
        self.eye.move_back()

    def rotate_left(self, event):
        self.eye.rotate_left()

    def rotate_right(self, event):
        self.eye.rotate_right()

    def add_segment(self, segment):
        assert isinstance(segment, Segment)
        self.segments.append(segment)

    def run(self):
        self.update()
        self.root.mainloop()

def make_cube(engine, rootx, rooty, rootz, size):
    size = float(size/2)
    seg1 = Segment(np.matrix([[rootx - size, rootx - size, rootx - size, rootx - size],[rooty - size, rooty - size, rooty + size, rooty + size],[rootz - size, rootz + size, rootz + size, rootz - size]]))
    seg2 = Segment(np.matrix([[rootx - size, rootx - size, rootx + size, rootx + size],[rooty - size, rooty - size, rooty - size, rooty - size],[rootz - size, rootz + size, rootz + size, rootz - size]]))
    seg3 = Segment(np.matrix([[rootx - size, rootx - size, rootx + size, rootx + size],[rooty - size, rooty + size, rooty + size, rooty - size],[rootz - size, rootz - size, rootz - size, rootz - size]]))
    seg4 = Segment(np.matrix([[rootx - size, rootx - size, rootx + size, rootx + size],[rooty - size, rooty + size, rooty + size, rooty - size],[rootz + size, rootz + size, rootz + size, rootz + size]]))
    seg5 = Segment(np.matrix([[rootx - size, rootx - size, rootx + size, rootx + size],[rooty + size, rooty + size, rooty + size, rooty + size],[rootz - size, rootz + size, rootz + size, rootz - size]]))
    seg6 = Segment(np.matrix([[rootx + size, rootx + size, rootx + size, rootx + size],[rooty - size, rooty - size, rooty + size, rooty + size],[rootz - size, rootz + size, rootz + size, rootz - size]]))

    engine.add_segment(seg1)
    engine.add_segment(seg2)
    engine.add_segment(seg3)
    engine.add_segment(seg4)
    engine.add_segment(seg5)
    engine.add_segment(seg6)

engine = Engine()
for x in range(-50,50,10):
    for y in range(40,50,10):
        for z in range(-50,50,10):
            make_cube(engine, x,y,z,2)
engine.run()
