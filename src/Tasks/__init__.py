#!/usr/bin/env python

import gtk
import time
import datetime

import cream.ipc
from cream.contrib.melange import api

@api.register('tasks')
class Tasks(api.API):

    def __init__(self):
        api.API.__init__(self)

        self.task_manager = cream.ipc.get_object('org.cream.PIM', 
                                    '/org/cream/pim/Tasks')
        builder = gtk.Builder()
        builder.add_from_file('add-dialog.glade')

        self.dialog = builder.get_object('dialog')
        self.dialog.connect('delete_event', self.dialog.hide)
        self.title = builder.get_object('title')
        self.description = builder.get_object('description').get_buffer()
        self.priority = builder.get_object('priority')
        self.deadline = builder.get_object('deadline')
        self.tags = builder.get_object('tags')
        self.calendar = builder.get_object('calendar')
        self.calendar_win = builder.get_object('calendar_win')
        self.calendar_win.connect('delete_event', self.calendar_win.hide)
        builder.get_object('calendar_btn').connect('clicked', self.show_calendar)

    @api.expose
    def add_task(self):
        '''Add a task to the database. The data is provided by the dialog.'''

        @api.in_main_thread
        def add_task():
            self.reset_dialog()
            if self.dialog.run() == 1:
                data = self.get_data()
                self.task_manager.add_task(data['title'], 
                    data['description'], data['tags'], data['priority'], 
                    data['deadline'])
            self.dialog.hide()

        add_task()

    @api.expose
    def edit_task(self, id):
        '''Edit a task with the given id.'''

        @api.in_main_thread
        def edit_task(id):
            task = self.task_manager.get_task(int(id))
            self.set_dialog_entries(task)
            if self.dialog.run() == 1:
                data = self.get_data()
                self.task_manager.edit_task(int(id), data['title'], 
                    data['description'], data['tags'], data['priority'], data['deadline'])
            self.dialog.hide()

        edit_task(id)

    @api.expose
    def set_task_status(self, id, status):
        '''Set the tasks status.'''

        @api.in_main_thread
        def set_task_status(id, status):
            self.task_manager.set_task_status(id, status)

        set_task_status(int(id), int(status))
        
    @api.expose
    def list_tasks(self):
        '''Get all tasks which are not marked as done.'''

        @api.in_main_thread
        def list_tasks():
            tasks = self.task_manager.list_tasks()
            tasks = filter(lambda task: task['status'] != 2, tasks)
            return map(self.convert_date_to_timedelta, sorted(tasks, key=lambda task: task['deadline']))
        
        return list_tasks()


    def convert_date_to_timedelta(self, task):
        today = datetime.date.fromtimestamp(time.time())
        deadline = datetime.date.fromtimestamp(task['deadline'])
        timedelta = abs((today - deadline).days)

        if today > deadline and timedelta < 8:
            if timedelta == 1:
                task['deadline'] = 'yesterday'
            else:
                task['deadline'] = '{0} days ago'.format(str(timedelta))
        elif today < deadline and timedelta < 8:
            if timedelta == 1:
                task['deadline'] = 'tomorrow'
            else:
                task['deadline'] = '{0} days left'.format(str(timedelta))
        elif today == deadline:
            task['deadline'] = 'today'
        else:
            task['deadline'] = '{0}.{1}.{2}'.format(deadline.day, deadline.month, deadline.year)
        return task

    def get_data(self):
        '''Retrieve the data from the dialog'''

        data = dict()
        data['title'] = self.title.get_text()
        data['description'] = self.description.get_text(
            self.description.get_start_iter(), self.description.get_end_iter())
        data['tags'] = self.tags.get_text()
        data['priority'] = self.priority.get_active()
        date = self.deadline.get_text()
        timestamp = int(time.mktime(time.strptime(date,'%d.%m.%Y' )))
        data['deadline'] = timestamp
        return data

    def set_dialog_entries(self, task):
        '''When editing a task, set the entries to edit them'''

        self.title.set_text(task['title'])
        self.description.set_text(task['description'])
        self.priority.set_active(task['priority'])
        timestamp = task['deadline']
        today = time.localtime(timestamp)[:3]
        self.calendar.select_month(today[1] -1, today[0])
        self.calendar.select_day(today[2])
        self.deadline.set_text('{0}.{1}.{2}'.format(today[2], today[1], today[0]))
        self.tags.set_text(task['category'])

    def reset_dialog(self):
        '''When adding a task, clear the dialog'''

        self.title.set_text('')
        self.description.set_text('')
        self.priority.set_active(-1)
        self.deadline.set_text('')
        today = time.localtime()
        self.calendar.select_month(today[1] -1, today[0])
        self.calendar.select_day(today[2])
        self.tags.set_text('')

    def show_calendar(self, widget, *args):
        '''Show the calendarwindow'''

        if self.calendar_win.run() == 1:
            date = self.calendar.get_date()
            self.deadline.set_text('{0}.{1}.{2}'.format(date[2], date[1] + 1, date[0]))
        self.calendar_win.hide()
