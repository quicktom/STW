import pyglet



# get a list of all controllers:
controllers = pyglet.input.get_controllers()

print(controllers)

if controllers:
    controller = controllers[0]
    controller.open()

    while 1:
        if controller.a:
            print("a")

@controller.event
def on_stick_motion(controller, name, x_value, y_value):

    if name == "leftstick":
        print("leftstick")
    elif name == "rightstick":
        print("rightstick")

@controller.event
def on_trigger_motion(controller, name, value):

    if name == "lefttrigger":
        print("lefttrigger")
    elif name == "righttrigger":
        print("righttrigger")