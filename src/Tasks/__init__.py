#!/usr/bin/env python


from cream.contrib.melange import api
import cream.ipc

import os.path
import gtk
import time

@api.register('tasks')
class Tasks(api.API):

    def __init__(self):
        api.API.__init__(self)

        self.task_manager = cream.ipc.get_object('org.cream.PIM', 
                                    '/org/cream/pim/Tasks')
        builder = gtk.Builder()
        builder.add_from_file(os.path.join(self.context.working_directory, 
                                                'add-dialog.glade'))

        self.dialog = builder.get_object('dialog')
        self.title = builder.get_object('title')
        self.description = builder.get_object('description').get_buffer()
        self.tags = builder.get_object('tags')
        self.priority = builder.get_object('priority')
        self.deadline = builder.get_object('deadline')

        list_store = gtk.ListStore(str)
        list_store.append(['Low']) 
        list_store.append(['Medium'])
        list_store.append(['High'])
        self.priority.set_model(list_store)
        cell = gtk.CellRendererText()
        self.priority.pack_start(cell)
        self.priority.add_attribute(cell,'text',0)

        self.calendar = builder.get_object('calendar')
        self.calendar.connect('day-selected-double-click', self.btn_cb, 1)
        
        self.calendar_win = builder.get_object('calendar_win')
        self.calendar_win.connect('delete_event', lambda w,e: self.calendar_win.hide())
        btn = builder.get_object('calendar_btn')
        btn.connect('clicked', self.show_calendar)

        btn = builder.get_object('ok_cal')
        btn.connect('clicked', self.btn_cb, 1)
        
        btn = builder.get_object('cancel_cal')
        btn.connect('clicked', self.btn_cb, -3)

        


    @api.expose
    def add_task(self):
        @api.in_main_thread
        def add_task():
            self.reset_dialog()
            response = self.dialog.run()
            if response == 1:
                data = self.get_data()
                self.dialog.hide()
                print data['deadline']
                return self.task_manager.add_task(data['title'], 
                    data['description'], data['tags'], data['priority'], 
                    data['deadline'])
            
            self.dialog.hide()

        add_task()


    @api.expose
    def edit_task(self, id):
        @api.in_main_thread
        def edit_task(id):
            task = self.task_manager.get_task(int(id))
            self.set_dialog_entries(task)
            response = self.dialog.run()
            if response == 1:
                data = self.get_data()
                self.dialog.hide()
                return self.task_manager.edit_task(int(id), data['title'], 
                    data['description'], data['tags'], data['priority'], data['deadline'])
            
            self.dialog.hide()

        edit_task(id)

    @api.expose
    def set_task_status(self, id, status):
        @api.in_main_thread
        def set_task_status(id, status):
            self.task_manager.set_task_status(id, status)

        set_task_status(int(id), int(status))
        

    @api.expose
    def list_tasks(self):
        @api.in_main_thread
        def list_tasks():
            tasks = self.task_manager.list_tasks()
            tasks = filter(lambda task: task['status'] != 2, tasks)
            return sorted(tasks, key=lambda task: task['deadline'])
        
        return list_tasks()




    def get_data(self):
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
        self.title.set_text('')
        self.description.set_text('')
        self.priority.set_active(-1)
        self.deadline.set_text('')
        today = time.localtime()
        self.calendar.select_month(today[1] -1, today[0])
        self.calendar.select_day(today[2])
        self.tags.set_text('')

    def show_calendar(self, widget, *args):
        response = self.calendar_win.run()
        self.calendar_win.hide()

        if response == 1:
            date = self.calendar.get_date()
            self.deadline.set_text('{0}.{1}.{2}'.format(date[2], date[1] + 1, date[0]))

    def btn_cb(self, widget, id):
        self.calendar_win.response(id)
