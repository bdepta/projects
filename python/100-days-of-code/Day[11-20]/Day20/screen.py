from turtle import Screen
class ScreenDefinition:
    def __init__(self):
        self.screen = Screen()
        self.screen_size = {
                "width" : 600,
                "height": 600
            }
        self.define_screen()
    
    def define_screen(self):
        self.screen.screensize(self.screen_size["width"],self.screen_size["height"])
        self.screen.bgcolor("Black")
        self.screen.title("Awesome Snake")
        self.screen.tracer(0)
        return self.screen
    
    def screen_listen(self):
        self.screen.listen()
    
    def screen_onkey(self,key,function):
        self.screen.onkey(key=key, fun=function)


    def screen_update(self):
        self.screen.update()
    
    def exit_on_click(self):
        self.screen.exitonclick()