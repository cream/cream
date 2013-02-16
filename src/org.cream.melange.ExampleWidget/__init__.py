from melange import api


# This will register the API-class as `widget.api.example`
# accessable from your JavaScript code.
@api.register('org.cream.melange.ExampleWidget')
class Example(api.API):

    def __init__(self):

        api.API.__init__(self)

    #This exposes the method which can be called in you JavaScript code as
    # `widget.api.doit(arg);`
    @api.expose
    def doit(self, arg):

        self.log("Got '{0}'...".format(arg))
        return arg.capitalize()
