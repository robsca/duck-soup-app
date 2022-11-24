import tkinter as tk
from math import sin, cos, pi

# link 1 ->
source = ['John', 'Mary', 'Peter', 'Susan', 'George', 'Jane', 'Thomas', 'Alice', 'Bob', 'Jill']
# create a window
window = tk.Tk()
window.title("Notebook")
window.geometry("500x500")

# create a canvas to draw on
canvas = tk.Canvas(window, width=500, height=500)
canvas.pack()

# cartesian coordinates 0,0 is in tkinter w//2 and h//2
def from_cartesian(x, y, w, h):
    return x + w//2, -y + h//2

def from_tk(x, y, w, h):
    return x - w//2, -y + h//2

def connect_line(circles):
    for i in range(len(circles)):
        for j in range(i + 1, len(circles)):
            # get the coordinates of the circles
            x1, y1, x2, y2 = canvas.coords(circles[i])
            xc1 = (x1 + x2) / 2
            yc1 = (y1 + y2) / 2
            x1, y1, x2, y2 = canvas.coords(circles[j])
            xc2 = (x1 + x2) / 2
            yc2 = (y1 + y2) / 2
            # create the line
            line = canvas.create_line(xc1, yc1, xc2, yc2)
            # add the line to the list
            lines.append(line)
                
# get width and height of the canvas
w = 500
h = 500
print(w, h)

# create a circle for each source

circles = []
circles_dict = {}
texts = []
lines = []
for i in range(len(source)):
    # create a circle
    x = 200 * cos(2 * pi * i / len(source))
    y = 200 * sin(2 * pi * i / len(source))
    circle = canvas.create_oval(from_cartesian(x, y, w, h), from_cartesian(x + 10, y + 10, w, h), fill="red")
    # add the circle to the list
    circles.append(circle)
    # create a text
    text = canvas.create_text(from_cartesian(x, y, w, h), text=source[i])
    # add the text to the list
    texts.append(text)
    # save the circle in a dictionary and the coordinates in a list
    circles_dict[circle] = [x, y]

# connect the circles
connect_line(circles)


# drag circle   
def drag(event):
    print("drag")
    # get the coordinates of the mouse
    x = event.x
    y = event.y
    # get the closest circle
    # get the distance between the mouse and the center of the circle
    distances = []
    for circle in circles:
        # get the center of the circle
        x1, y1, x2, y2 = canvas.coords(circle)
        xc = (x1 + x2) / 2
        yc = (y1 + y2) / 2
        # calculate the distance
        distance = ((x - xc) ** 2 + (y - yc) ** 2) ** 0.5
        # add the distance to the list
        distances.append(distance)
    # get the index of the closest circle
    index = distances.index(min(distances))
    # move the circle
    canvas.coords(circles[index], x - 5, y - 5, x + 5, y + 5)

    # move the text
    canvas.coords(texts[index], x, y)

    # connect the circles
    # delete the lines
    for line in lines:
        canvas.delete(line)

    connect_line(circles)

# double click original position
def double_click(event):
    print("double click")
    # get the coordinates of the mouse
    x = event.x
    y = event.y
    # get the closest circle
    # get the distance between the mouse and the center of the circle
    distances = []
    for circle in circles:
        # get the center of the circle
        x1, y1, x2, y2 = canvas.coords(circle)
        xc = (x1 + x2) / 2
        yc = (y1 + y2) / 2
        # calculate the distance
        distance = ((x - xc) ** 2 + (y - yc) ** 2) ** 0.5
        # add the distance to the list
        distances.append(distance)
    # get the index of the closest circle
    index = distances.index(min(distances))
    x, y = circles_dict[circles[index]]
    # translate the circle
    x, y = from_cartesian(x, y, w, h)  
    canvas.coords(circles[index], x - 5, y - 5, x + 5, y + 5)
    # translate the text
    canvas.coords(texts[index], x, y)
    

    # connect the circles
    # delete the lines
    for line in lines:
        canvas.delete(line)

    connect_line(circles)

# bind the mouse to the canvas
canvas.bind("<B1-Motion>", drag)
canvas.bind("<Double-Button-1>", double_click)
# bind the drag function to the mouse click and drag
canvas.bind("<B1-Motion>", drag)

# run the window's main loop

window.mainloop()