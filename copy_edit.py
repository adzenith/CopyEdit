import sublime, sublime_plugin
import CopyEdit.pyperclip as pyperclip

selection_strings = []


def print_status_message(verb, numregions=None):
	numregions = numregions or len(selection_strings)
	numchars = sum([len(s) for s in selection_strings])
	message = "{} {} character{}".format(verb, numchars, 's' if numchars != 1 else '')
	if numregions > 1:
		message += " over {} selection regions".format(numregions)
	sublime.status_message(message)

##TODO: read copy-whole-line option or whatever
class CopyEditCommand(sublime_plugin.TextCommand):
	def copy(self, edit):
		if sum([len(s) for s in self.view.sel()]) == 0:
			return False
		
		selection_strings.clear()
		for s in self.view.sel():
			selection_strings.append(self.view.substr(s))
		pyperclip.copy('\n'.join(selection_strings))
		return True
	
	def run(self, edit, verb="Copied"):
		if self.copy(edit):
			print_status_message(verb)

class CutEditCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.run_command("copy_edit", args={"verb":"Cut"})
		for s in self.view.sel():
			self.view.erase(edit, s)

class PasteEditCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		
		#check if clipboard is more up to date
		pasteboard = pyperclip.paste()
		from_clipboard = False
		if pasteboard != '\n'.join(selection_strings):
			selection_strings.clear()
			selection_strings.extend(pasteboard.split('\n'))
			from_clipboard = True
		
		print(selection_strings)
		numstrings = len(selection_strings)
		numsels = len(self.view.sel())
		if numsels == 0:
			return
		
		if numstrings <= numsels and numsels % numstrings == 0:
			strs_per_sel = 1
		elif numsels < numstrings and numstrings % numsels == 0:
			strs_per_sel = int(numstrings / numsels)
		else:
			strs_per_sel = numstrings
		
		str_index = 0
		new_sels = []
		for sel in self.view.sel():
			self.view.erase(edit, sel)
			insertion_point = sel.begin()
			for string in selection_strings[str_index:str_index+strs_per_sel]:
				self.view.insert(edit, insertion_point, string)
				insertion_point += len(string)
				region = sublime.Region(insertion_point)
				new_sels.append(region)
			str_index = (str_index + strs_per_sel) % numstrings
		
		print_status_message("Pasted", len(self.view.sel()))
		
		self.view.sel().clear()
		for s in new_sels:
			self.view.sel().add(s)
