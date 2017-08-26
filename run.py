from Tkinter import *
import numpy as np
import math

class Segment():
    def __init__(self
                , matrix=np.matrix([])
                , color=''):
        '''
        A Segment is a single component in a Cluster. The verticies in the
        Segments are converted by the rederer into canvas polygon coordinates.

        Args:
              matrix: a numpy matrix composed of vectors representing the x,y,z 
                      values of the verticies of the Segment

                      example: np.matrix([[1,2,3],[4,5,6],[7,8,9]])
                               That matrix looks like this:
                               1 2 3
                               4 5 6
                               7 8 9

                               this represents a Segment with verticies
                               (x=1,y=4,z=7),(2,5,8),(3,6,9)

              color: the color of the segment

                     format: 'color' | '#<hex color value>'
        '''
        self.matrix = matrix
        self.color = color

    def to_vectors(self):
        for i in range(len(self.matrix[0,:].tolist()[0])):
            yield self.matrix[:,i]

    def to_coords(self):
        for vect in self.to_vectors():
            yield vect.ravel().tolist()[0]


    def center_point(self):
        avg_x = 0
        avg_y = 0
        avg_z = 0
        num_points = len(self.matrix[0,:].tolist()[0])

        for x in self.matrix[0,:].ravel().tolist()[0]:
            avg_x += x

        for y in self.matrix[1,:].ravel().tolist()[0]:
            avg_y += y

        for z in self.matrix[2,:].ravel().tolist()[0]:
            avg_z += z

        avg_x /= num_points
        avg_y /= num_points
        avg_z /= num_points

        return [avg_x, avg_y, avg_z]

class Cluster():
    def __init__(self
                , segments):
        '''
        A Cluster is a group of Segments. It represents an object in the Engine.

        Args:
              segments: a list of the Segments in this Cluster
        '''
        self.segments = segments


class Eye():
    def __init__(self
                , location=np.matrix([[0.0],[0.0],[69.0]])
                , canvas_center=[960,840]
                , scale=500):
        '''
        The Eye is the object that 'sees' the Clusters and translates them into
        canvas coordinates to draw on the screen. The Engine passes an Eye the
        clusters and the Eye will render its view of the Clusters. How the
        Clusters are rendered depends on the Eyes location, rotation, scale, etc

        Args:
              location: a numpy matrix that is a vector representing the Eyes
                        location

                        example: np.matrix([[1],[2],[3]])
                                 this is a vector representing point (1,2,3), so
                                 this Eyes location would be: x=1, y=2, z=3

              canvas_center: the center of the Engine canvas

              scale: the size of 1 world unit in pixles

              theta: the inital rotation of the eye in radians
        '''
        self.location = location
        self.scale = scale
        self.canvas_center = canvas_center
        self.theta_y = 0.0
        self.theta_z = 0.0

    def render(self, clusters=[]):
        for seg in self.process_clusters(clusters):
            coords = []
            for coord in seg.to_coords():
                try:
                    xp = (coord[1] / -coord[0]) * self.scale
                    yp = (coord[2] / -coord[0]) * self.scale
                    coords += [self.canvas_center[0] + xp, self.canvas_center[1] + yp]
                except(ZeroDivisionError):
                    pass

            yield {'coords':coords, 'color':seg.color}

    def process_clusters(self, clusters):
        for cluster in clusters:
            for seg in cluster.segments:
                adjusted_seg = self.adjust_seg(seg)
                quad = get_quadrant(adjusted_seg.center_point())
                if quad in [1,4,5,8]:
                    yield adjusted_seg

    def adjust_seg(self, seg):
        adjusted_matrix = seg.matrix - self.location
        adjusted_matrix = np.dot(self.rotation_z(), adjusted_matrix)
        adjusted_matrix = np.dot(self.rotation_y(), adjusted_matrix)
        return Segment(adjusted_matrix, seg.color)

    def rotation_z(self):
        return np.matrix([
                        [math.cos(self.theta_z),math.sin(self.theta_z),0]
                       ,[-math.sin(self.theta_z),math.cos(self.theta_z),0]
                       ,[0,0,1]
                    ])

    def rotation_y(self):
        return np.matrix([
                        [math.cos(self.theta_y),0,-math.sin(self.theta_y)]
                       ,[0,1,0]
                       ,[math.sin(self.theta_y),0,math.cos(self.theta_y)]
                    ])

    def move_left(self):
        self.location += np.matrix([[0.0],[30.0],[0.0]])

    def move_right(self):
        self.location += np.matrix([[0.0],[-30.0],[0.0]])

    def move_forward(self):
        self.location += np.matrix([[30.0],[0.0],[0.0]])

    def move_back(self):
        self.location += np.matrix([[-30.0],[0.0],[0.0]])

    def rotate_right(self):
        self.theta_z += float(math.pi / 100)
        if self.theta_z > 2 * math.pi:
            self.theta_z -= (2 * math.pi)
        elif self.theta_z < 0:
            self.theta_z += (2 * math.pi)

    def rotate_left(self):
        self.theta_z -= float(math.pi / 100)
        if self.theta_z > 2 * math.pi:
            self.theta_z -= (2 * math.pi)
        elif self.theta_z < 0:
            self.theta_z += (2 * math.pi)

    def rotate_up(self):
        self.theta_y += float(math.pi / 100)
        if self.theta_y > math.pi/2:
            self.theta_y = math.pi/2

    def rotate_down(self):
        self.theta_y -= float(math.pi / 100)
        if self.theta_y < -math.pi/2:
            self.theta_y = -math.pi/2


class Engine():
    def __init__(self):
        '''
        This is the graphics Engine. It is reposnsible for keeping track of and
        upating the Clusters. It is also reponsible for keeping track of an Eye
        (Or multiple eyes). It uses an Eye to render the Clusters. The Engine is
        reponsible for the UI. It draws the screen and manages all the tkinter
        things.

        '''
        self.update_delay =  10 #milliseconds
        self.root = Tk()
        self.root.attributes('-fullscreen', True)
        self.root.config(bg='black', highlightbackground='black')
        self.canvas = Canvas(self.root, height=1080, width=1920, bg='#2f343f', highlightbackground='#2f343f')
        self.canvas.pack()
        self.eye = Eye()
        self.clusters = []
        self.rotate_val = None

        self.root.bind('w', self.move_forward)
        self.root.bind('a', self.move_left)
        self.root.bind('s', self.move_back)
        self.root.bind('d', self.move_right)

        self.root.bind('<Button-1>', self.rotate_begin)
        self.root.bind('<B1-Motion>', self.rotate)

    def update(self):
        self.canvas.delete('all')
        self.canvas.create_text(30,10,text=str([val/30 for val in self.eye.location.ravel().tolist()[0]]))
        for polygon in self.eye.render(self.clusters):
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

    def rotate_begin(self, event):
        self.rotate_val = [event.x, event.y]

    def rotate(self, event):
        if (self.rotate_val[0] < event.x):
            self.eye.rotate_left()
        elif (self.rotate_val[0] > event.x):
            self.eye.rotate_right()

        if (self.rotate_val[1] < event.y):
            self.eye.rotate_up()
        elif (self.rotate_val[1] > event.y):
            self.eye.rotate_down()

        self.rotate_val = [event.x, event.y]

    def add_cluster(self, cluster):
        assert isinstance(cluster, Cluster)
        self.clusters.append(cluster)

    def run(self):
        self.update()
        self.root.mainloop()


def get_quadrant(point=[]):
    '''
    Helper function that figures out what 2d quadrant a point is in
    and return the number

    Args:
          x: the x coordinate
          y: the y coordinate
    '''
    x = point[0]
    y = point[1]
    z = point[2]

    if x > 0:
        if y > 0:
            if z > 0:
                return 1
            elif x < 0:
                return 5
            else:
                return 1
        elif y < 0:
            if z > 0:
                return 4
            elif z < 0:
                return 8
            else:
                return 4
        else:
            if z > 0:
                return 2
            elif z < 0:
                return 7
            else:
                return 2
    elif x < 0:
        if y > 0:
            if z > 0:
                return 2
            elif z < 0:
                return 6
            else:
                return 2
        elif y < 0:
            if z > 0:
                return 3
            elif z < 0:
                return 7
            else:
                return 3
        else:
            if z > 0:
                return 2
            elif z < 0:
                return 7
            else:
                return 2
    else:
        if y > 0:
            if z > 0:
                return 2
            elif z < 0:
                return 6
            else:
                return 2
        elif y < 0:
            if z > 0:
                return 4
            elif z < 0:
                return 8
            else:
                return 4
        else:
            if z > 0:
                return 2
            elif z < 0:
                return 6
            else:
                return -1


################################################################################
##              debugging stuffs                                              ##
################################################################################


def make_cube(engine, rootx, rooty, rootz, size):
    '''
    Makes a cube in 'engine' at point (rootx,rooty,rootz) with the given size

    Args:
          engine: the Engine object to make the cube in
          rootx: the x coordinate for the center of the cube
          rooty: the y coordinate for the center of the cube
          rootz: the z coordinate for the center of the cube
          size: the size of an edge on the cube
    '''
    size = float(size/2)

    seg1 = Segment(np.matrix([
                        [rootx - size, rootx - size, rootx - size, rootx - size]
                       ,[rooty - size, rooty - size, rooty + size, rooty + size]
                       ,[rootz - size, rootz + size, rootz + size, rootz - size]
                    ]), 'red')

    seg2 = Segment(np.matrix([
                        [rootx - size, rootx - size, rootx + size, rootx + size]
                       ,[rooty - size, rooty - size, rooty - size, rooty - size]
                       ,[rootz - size, rootz + size, rootz + size, rootz - size]
                    ]), 'orange')

    seg3 = Segment(np.matrix([
                        [rootx - size, rootx - size, rootx + size, rootx + size]
                       ,[rooty - size, rooty + size, rooty + size, rooty - size]
                       ,[rootz - size, rootz - size, rootz - size, rootz - size]
                    ]), 'yellow')

    seg4 = Segment(np.matrix([
                        [rootx - size, rootx - size, rootx + size, rootx + size]
                       ,[rooty - size, rooty + size, rooty + size, rooty - size]
                       ,[rootz + size, rootz + size, rootz + size, rootz + size]
                    ]), 'green')

    seg5 = Segment(np.matrix([
                        [rootx - size, rootx - size, rootx + size, rootx + size]
                       ,[rooty + size, rooty + size, rooty + size, rooty + size]
                       ,[rootz - size, rootz + size, rootz + size, rootz - size]
                    ]), 'blue')

    seg6 = Segment(np.matrix([
                        [rootx + size, rootx + size, rootx + size, rootx + size]
                       ,[rooty - size, rooty - size, rooty + size, rooty + size]
                       ,[rootz - size, rootz + size, rootz + size, rootz - size]
                    ]), 'purple')

    engine.add_cluster(Cluster([seg1,seg2,seg3,seg4,seg5,seg6]))


engine = Engine()
#for x in range(60,80,10):
#    for y in range(-10,10,10):
#        for z in range(60,80,10):
#            make_cube(engine, x,y,z,9)

make_cube(engine, 0, 0, 0, 2)
make_cube(engine, 1, 0, 0, 2)
make_cube(engine, 0, 1, 0, 2)
make_cube(engine, 0, 0, 1, 2)

engine.run()
