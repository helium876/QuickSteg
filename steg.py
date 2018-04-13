from __future__ import absolute_import, unicode_literals
import __builtin__
import sys
import os
from PyQt4 import QtCore, QtGui, uic


#Custom Steganography Libraries
import StegImgLib
import StegAudLib
import StegVidLib

qtCreatorFile = "Quick_Steg.ui" # Enter file here.
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class PopupDialog(QtGui.QDialog):
	def __init__(self, parent=None):
		pass
        
class Application(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self):
		super(Application, self).__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

		self.ui.browse_1.clicked.connect(self.browse_1_action)
		self.ui.browse_2.clicked.connect(self.browse_2_action)

		self.ui.reset_1.clicked.connect(self.reset_1_action)
		self.ui.reset_2.clicked.connect(self.reset_2_action)

		self.ui.hide_message.clicked.connect(self.hide_message_action)
		self.ui.show_hidden_message.clicked.connect(self.show_hide_message_action)

	def browse_1_action(self):
		file_name = QtGui.QFileDialog.getOpenFileName(self, 'Pick a file', 
			'c:\\',"All files (*)")
		self.ui.write_path.setText(file_name)

	def browse_2_action(self):
		file_name = QtGui.QFileDialog.getOpenFileName(self, 'Pick a file', 
			'c:\\',"All files (*)")
		self.ui.read_path.setText(file_name)

	def reset_1_action(self):
		self.ui.write_path.clear()
		self.ui.message.clear()

	def reset_2_action(self):
		self.ui.read_path.clear()
		self.ui.hidden_message.clear()

	def hide_message_action(self):
		# try:
		msg = self.ui.message.toPlainText()
		file_path = self.ui.write_path.text()
		# if file_path is '':
		# 	raise FileNotFoundError('[Errno 2] No such file or directory: \'\'')
		# if not os.path.exists(file_path):
		# 	raise FileNotFoundError('[Errno 2] No such file or directory: file_path')
		# if not str(msg):
		# 	raise ValueError('No value present in message')
		self.write_hidden_msg(file_path, msg)
		# except FileNotFoundError as fnfe:
		# 	self.showdialog('Error', 'Invaild File Path.', detailed_text = str(fnfe))
		# except ValueError as ve:
		# 	self.showdialog('Error', 'Message can not be empty', detailed_text = str(ve))
		# except StegImgLib.SteganographyImageException as sie:
		# 		self.showdialog('Error', 'Steganography Image Error', detailed_text = str(sie))
		# except Exception as e:
		# 	self.showdialog('Error', 'An Unexcepted Error Occured', detailed_text = str(e))			

	def show_hide_message_action(self):
		try:
			if self.ui.read_path.text() is '':
				raise FileNotFoundError('[Errno 2] No such file or directory: \'\'')
			self.read_hidden_msg(self.ui.read_path.text())
		# except FileNotFoundError:
			# self.showdialog('Error', 'Please enter that the file path is corrected Or Enter attach a hidden message to the file.', detailed_text = str(fnfe))
		except StegImgLib.SteganographyImageException as sie:
				self.showdialog('Error', 'Steganography Image Error', detailed_text = str(sie))
		except Exception as e:
			self.showdialog('Error', 'An Unexcepted Error Occured', detailed_text = str(e))

	
	def showdialog(self, title, text, informative_text = '', detailed_text = ''):
		msg = QtGui.QMessageBox()
		msg.setIcon(QtGui.QMessageBox.Critical)

		msg.setText(text)
		if informative_text is not '':
			msg.setInformativeText(informative_text)
		msg.setWindowTitle(title)
		if detailed_text is not '':
			msg.setDetailedText(detailed_text)
		msg.setStandardButtons(QtGui.QMessageBox.Ok)
		msg.exec_()

	def showCompleted(self):
		msg = QtGui.QMessageBox()
		msg.setIcon(QtGui.QMessageBox.Information)
		msg.setText("Your message is completely hidden")
		msg.setWindowTitle("Completed")
		msg.setStandardButtons(QtGui.QMessageBox.Ok)
		msg.exec_()

	def read_hidden_msg(self, file_path):
		if(self.isImage(file_path)):
			steg = StegImgLib.StegImg()
			self.ui.hidden_message.setText(''.join([str(char) for char in steg.retr(file_path)]))
		elif(self.isVideo(file_path)):
			steg = StegVidLib.StegVid()
			steg.show(file_path)
			self.ui.hidden_message.setText(''.join([str(char) for char in steg.show(file_path)]))
		elif(self.isAudio(file_path)):
			steg = StegAudLib.StegAud()
			self.ui.hidden_message.setText(steg.decode(file_path))
		else:
			raise ValueError('File not supported')

	def write_hidden_msg(self, file_path, msg):
		if(self.isImage(file_path)):
			steg = StegImgLib.StegImg()
			steg.hide(file_path, msg)
			self.showCompleted()
		elif(self.isVideo(file_path)):
			steg = StegVidLib.StegVid()
			steg.hide(file_path,msg)
			self.showCompleted()
		elif(self.isAudio(file_path)): 
			steg = StegAudLib.StegAud()
			steg.encode(file_path, msg)
			self.showCompleted()
		else:
			raise ValueError('File not supported')

	def isImage(self, file_path):
		file_path = str(file_path)
		file_path = file_path.lower()
		if(file_path.endswith('.gif') or file_path.endswith('.jpg') or file_path.endswith('.png') or file_path.endswith('.bmp')):
			return True
		return False

	def isVideo(self, file_path):
		file_path = str(file_path)
		file_path = file_path.lower()
		if(file_path.endswith('.mp4') or file_path.endswith('.webm') or file_path.endswith('.avi')):
			return True
		return False

	def isAudio(self, file_path):
		file_path = str(file_path)
		file_path = file_path.lower()
		if(file_path.endswith('.wav')):
			return True
		return False

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec_())