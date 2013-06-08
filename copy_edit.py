import sublime, sublime_plugin
import CopyEdit.pyperclip as pyperclip

selection_strings = []


##TODO: read copy-whole-line option or whatever
class CopyEditCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		selection_strings.clear()
		for s in self.view.sel():
			selection_strings.append(self.view.substr(s))
		pyperclip.copy('\n'.join(selection_strings))
		numchars = sum([len(s) for s in selection_strings])
		message = "Copied {} characters".format(numchars)
		if len(selection_strings) > 1:
			message += " over {} selection regions".format(len(selection_strings))
		sublime.status_message(message)

class CutEditCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.run_command("copy_edit")
		for s in self.view.sel():
			self.view.erase(edit, s)

class PasteEditCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		#check if clipboard is more up to date
		pasteboard = pyperclip.paste()
		joiner = ''
		if pasteboard != '\n'.join(selection_strings):
			selection_strings.clear()
			selection_strings.extend(pasteboard.split('\n'))
			joiner = '\n'
		
		print(selection_strings)
		numstrings = len(selection_strings)
		numsels = len(self.view.sel())
		if numstrings == numsels:
			for sel, string in zip(self.view.sel(), selection_strings):
				self.view.erase(edit, sel)
				self.view.insert(edit, sel.begin(), string)
		if numstrings < numsels and numsels % numstrings == 0:
			str_index = 0
			for sel in self.view.sel():
				self.view.erase(edit, sel)
				self.view.insert(edit, sel.begin(), selection_strings[str_index])
				str_index = (str_index + 1) % numstrings
		if numsels < numstrings and numstrings % numsels == 0:
			strs_per_sel = int(numstrings / numsels)
			str_index = 0
			for sel in self.view.sel():
				self.view.erase(edit, sel)
				insertion = joiner.join(selection_strings[str_index:str_index+strs_per_sel])
				self.view.insert(edit, sel.begin(), insertion)
				str_index += strs_per_sel
		
		
		#empty all sels