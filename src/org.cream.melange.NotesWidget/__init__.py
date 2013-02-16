import os

from melange import api


@api.register('org.cream.melange.NotesWidget')
class Notes(api.API):

    def __init__(self):
        api.API.__init__(self)

        self.notes_file = os.path.join(self.context.get_user_path(), 'notes.txt')

    @api.expose
    def save_notes(self, notes):

        with open(self.notes_file, 'w') as file_handle:
            file_handle.write(notes)

    @api.expose
    def get_notes(self):

        if not os.path.exists(self.notes_file):
            return ''

        with open(self.notes_file, 'r') as file_handle:
             return file_handle.read()
