from turtle import Screen

SCREEN_SIZE = {
                "width" : 450,
                "height": 300
            }


class ScreenDefinition:
    def __init__(self):
        self.screen = Screen()
        self.define_screen()
    
    def define_screen(self):
        self.screen.setup((2*SCREEN_SIZE["width"]),(2*SCREEN_SIZE["height"]))
        self.screen.bgcolor("Black")
        self.screen.title("Awesome Pong")
        self.screen.tracer(0)
    
    def screen_listen(self):
        self.screen.listen()
    
    def screen_onkey(self,key,function):
        self.screen.onkey(key=key, fun=function)


    def screen_update(self):
        self.screen.update()
    
    def exit_on_click(self):
        self.screen.exitonclick()