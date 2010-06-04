from cream.contrib.melange import api


# This will register the API-class as `widget.api.example`
# accessable from your JavaScript code.
@api.register('example')
class Example(api.API):

    def __init__(self):
           
        api.API.__init__(self)
 
    #This exposes the method which can be called in you JavaScript code as 
    # `widget.api.example.doit(arg);`
    @api.expose
    def doit(self, arg):

        print "Got '{0}'...".format(arg)
        return arg.capitalize()
