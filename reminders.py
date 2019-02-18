#import console
import reminders
#import time
import ui

class MyTableViewDataSource (object):
	def __init__(self):
		self.list_names = ['!nbox', 'Next Actions', 'Projects', 'Someday Maybe', 'WaitingFor']
		self.cal_dict = {}
		self.rem_dict = {}
		self.table_array = self.get_items()	
		
	def get_cal(self,section):
		return self.cal_dict[str(section)]
		
	def get_rem(self,section,row):
		return self.rem_dict[str(section)][row]
		
	def get_items(self):
		tmp = []
		for n in self.list_names:
			tmp.append([])
			
		cals = reminders.get_all_calendars()
		for c in cals:
			#print(c.title)
			if c.title in self.list_names:
				section = self.list_names.index(c.title)
				self.cal_dict[str(section)] = c
				#print('{} is section number {}'.format(c.title, section))
				self.rem_dict[str(section)] = reminders.get_reminders(calendar=c,completed=False)
				tmplist = []
				for r in self.rem_dict[str(section)]:
					#print(r)
					im = ui.Image('iob:drag_24')
					tmplist.append({'title':r.title, 'image':im, 'accessory_type': 'disclosure_indicator', 'subtitle': r.notes})
				tmp[section] = tmplist
					
			#print('=========')
		return tmp
		
	def tableview_number_of_sections(self, tableview):
		# Return the number of sections (defaults to 1)
		return len(self.list_names)

	def tableview_number_of_rows(self, tableview, section):
		# Return the number of rows in the section
		return len(self.table_array[section])

	def tableview_cell_for_row(self, tableview, section, row):
		# Create and return a cell for the given section/row
		cell = ui.TableViewCell(style='default')
		#cell.text_label.text = self.table_array[section][row]['title']
		cell.accessory_type = 'detail_button'
		cell.text_label.text = self.get_rem(section,row).title
		#cell.detail_text_label.text = self.table_array[section][row]['subtitle']
		return cell

	def tableview_title_for_header(self, tableview, section):
		# Return a title for the given section.
		# If this is not implemented, no section headers will be shown.
		return self.list_names[section]

	def tableview_can_delete(self, tableview, section, row):
		# Return True if the user should be able to delete the given row.
		return True

	def tableview_can_move(self, tableview, section, row):
		# Return True if a reordering control should be shown for the given row (in editing mode).
		return True

	def tableview_delete(self, tableview, section, row):
		# Called when the user confirms deletion of the given row.
		pass

	def tableview_move_row(self, tableview, from_section, from_row, to_section, to_row):
		# Called when the user moves a row with the reordering control (in editing mode).
		print('moving from [{}][{}] to [{}][{}]'.format(from_section, from_row, to_section, to_row))
		if to_section != from_section:
			try:
				r_old = self.get_rem(from_section,from_row)
				print(r_old)
				r_new = reminders.Reminder(self.get_cal(to_section))
				print('r_new: {}'.format(dir(r_new)))
				r_new.title = r_old.title
				if r_old.notes is not None:
					r_new.notes = r_old.notes
				r_new.completed = r_old.completed
				r_new.completion_date = r_old.completion_date
				r_new.due_date = r_old.due_date
				if r_old.alarms is not None:
					r_new.alarms = r_old.alarms
				print('new reminder created')
				r_new.save()
				keys = ['alarms', 'completed', 'completion_date', 'due_date', 'notes', 'title']
				for k in keys:
					print('{}: {}'.format(k,r_new.__getattribute__(k)))
				reminders.delete_reminder(r_old)
				#console.show_activity()
				#tableview.superview.a.start()
				#tableview.superview.a.bring_to_front()
				self.table_array = self.get_items()
				#time.sleep(5)
				#console.hide_activity()
				#tableview.superview.a.stop()
				tableview.reload_data()
			except:
				raise
				print('move failed')
		
class MyTableViewDelegate (object):
	def tableview_did_select(self, tableview, section, row):
		# Called when a row was selected.
		pass

	def tableview_did_deselect(self, tableview, section, row):
		# Called when a row was de-selected (in multiple selection mode).
		pass

	def tableview_title_for_delete_button(self, tableview, section, row):
		# Return the title for the 'swipe-to-***' button.
		return 'Complete'

class MyUI(ui.View):
	def __init__(self):
		tv = ui.TableView(name='root_table')
		self.name = 'My Lists'
		#things = self.get_items()
		#ds = ui.ListDataSource(items=things)
		tv.data_source = MyTableViewDataSource()
		tv.delegate = MyTableViewDelegate()
		self.add_subview(tv)
		tv.editing = False
		
		self.list_choices = ['Projects', 'Someday Maybe', 'Waiting For', '!nbox']
		
		for l in self.list_choices: 
			name = 'b'+l.replace(' ','')
			self.add_subview( ui.Button(name=name) )
			self[name].title = l
			self[name].background_color = 'white'
			self[name].font = ('<system-bold>', 18)
		
		rb = ui.ButtonItem(title='Edit')
		rb.action = self.edit_button
		self.right_button_items = [rb]
		
		self.a = ui.ActivityIndicator()
		self.add_subview(self.a)
		
	def edit_button(self, sender):
		if self['root_table'].editing == False:
			self['root_table'].editing = True
			self.right_button_items[0].title = 'Done'
		else:
			self['root_table'].editing = False
			self.right_button_items[0].title = 'Edit'
			
	def layout(self):
		if self.width < self.height:
			table_panel_width = self.width
			table_panel_height = self.height - 200
			button_panel_width = self.width
			button_width = button_panel_width/2
			button_height = 100
			button_panel_x0 = 0
			tmp_x = button_panel_x0
			tmp_y = self.height - 200		
		else:
			table_panel_width = self.width - 300
			table_panel_height = self.height
			button_panel_width = 300
			button_width = 300
			button_height = self.height / 4
			button_panel_x0 = table_panel_width
			tmp_x = button_panel_x0
			tmp_y = 0		
		
		self['root_table'].width = table_panel_width
		self['root_table'].height = table_panel_height
		
		for l in self.list_choices:
			name = 'b'+l.replace(' ','')
			self[name].x = tmp_x
			self[name].y = tmp_y
			self[name].width = button_width
			self[name].height = button_height
			if tmp_x < (button_panel_width-button_width):
				tmp_x = tmp_x + button_width
			else:
				tmp_x = button_panel_x0
				tmp_y = tmp_y + button_height
		'''
		self['bSomedayMaybe'].x = 0
		self['bSomedayMaybe'].y = 
		self['bSomedayMaybe'].width = self.width/2
		self['bSomedayMaybe'].height = 100
		self['bWaitingFor'].x = self.width/2
		self['bWaitingFor'].y = self.height - 200
		self['bWaitingFor'].width = self.width/2
		self['bWaitingFor'].height = 100
		'''
	
if __name__ == '__main__':
	v = MyUI()
	v.present('sheet')
