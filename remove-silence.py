#!/usr/bin/python

from sys import argv
from sys import exit
import os
from time import time
from sndhdr import what
import wave
sys_arguments = argv
sys_arguments.pop(0)

# basic script info
if not len(sys_arguments):
	print("\033[95m──────── Silence Removal Script ────────\033[0m")
	print("This script is used to delete silence from audio files, and can be used on wave (.wav) or MPEG-2 (.mp2) audio files.")
	print("To view information on how to use this script, run it with '-h' or '--help' after the script name.")
	exit()

# help
def show_help():
	print("\n\033[95m──────── Animation Optimization Usage ────────\033[0m")
	print("This script is used to delete silence from audio files. The script is compatible with wav type audio files.")
	print("To remove the silence from a, run the script with the path to the anigif you want to optimize after the script name. You can also put a path to a directory to modify all of the audio files within it. By default, modified files will be saved as copies. That way, just in case the script does something that messes up the file, you still have the original. It's a good idea to make sure the audio still sounds right after using the script.")
	print("\n\033[95m──────── Arguments ────────\033[0m")
	print("-h, --help")
	print("	Display this menu. This argument overrides all other operations, regardless of what other arguments are used.")
	print("-d, --disposal <none|trash|overwrite>")
	print("	What to do with the original file.")
	print("	none ────── Leave untouched and create a copy with '-unsilenced' at the end of the name. (default)")
	print("	trash ───── Move to trash and replace with the modified file.")
	print("	overwrite ─ Overwrite originals. I strongly advise against using this. This script is not perfect, and may make mistakes!")
	print("-l, --length <positive integer>")
	print("	The minimum length (in samples) required for silence. This doesn't affect trimming the start or end. This is important to make sure that nodes in waves aren't removed. (default 1000)")
	print("-m, --mode <all|middle|start|end|trim>")
	print("	Where silence should be removed.")
	print("	all ──── anywhere (default)")
	print("	middle ─ between sound")
	print("	start ── before sound begins")
	print("	end ──── after sound ends")
	print("	trim ─── before sound begins & after sound ends")
	print("-r, --recursive")
	print("	Also look in subdirectories when given a directory.")
	print("-t, --tolerance <float 0-1>")
	print("	The maximum value allowed to still be considered silence. (default 0)")
	print("-v, --verbosity <integer 0-4>")
	print("	How much information will be printed.")
	print("	0 ─ nothing (not recommended)")
	print("	1 ─ errors only")
	print("	2 ─ + error tips & reading/saving")
	print("	3 ─ + data removal stats (default when given directory)")
	print("	4 ─ all available info (default when given document)")
	exit()

# get arguments
arguments = []
disposal = 'none'
length_string = '1000'
mode = 'all'
recursive = False
tolerance_string = '0'
verbosity_string = ''

while len(sys_arguments):
	# argument
	if sys_arguments[0][0] == '-':
		if sys_arguments[0] == '-h' or sys_arguments[0] == '--help': show_help()
		elif sys_arguments[0] == '-d' or sys_arguments[0] == '--disposal': disposal = sys_arguments.pop(1)
		elif sys_arguments[0] == '-l' or sys_arguments[0] == '--length': min_length_string = sys_arguments.pop(1)
		elif sys_arguments[0] == '-m' or sys_arguments[0] == '--mode': mode = sys_arguments.pop(1)
		elif sys_arguments[0] == '-r' or sys_arguments[0] == '--recursive': recursive = True
		elif sys_arguments[0] == '-t' or sys_arguments[0] == '--tolerance': tolerance_string = sys_arguments.pop(1)
		elif sys_arguments[0] == '-v' or sys_arguments[0] == '--verbosity': verbosity_string = sys_arguments.pop(1)
		else:
			print(f"\033[93mERROR: '{sys_arguments[0]}' is not a recognized argument!\033[0m\nSee help (-h or --help) for information on arguments.")
			exit()
	# positional argument
	else: arguments.append(sys_arguments[0])
	# remove argument
	sys_arguments.pop(0)

del show_help
del sys_arguments

error = False

# get verbosity
if verbosity_string:
	try:
		verbosity = int(verbosity_string)
		if verbosity < 0 or verbosity > 4: raise ValueError
	except ValueError:
		error = True
		print(f"\033[93m[ERROR] '{verbosity_string}' is not a valid verbosity!\033[0m")
		print("Verbosity must be an integer from 0 to 4.\nSee help (-h or --help) for more info on arguments.")
		verbosity = 4
elif len(arguments) and os.path.isdir(arguments[0]): verbosity = 3
else: verbosity = 4
del verbosity_string

# get tolerance
try:
	tolerance = float(tolerance_string)
	if tolerance < 0 or tolerance > 1: raise ValueError
except ValueError:
	error = True
	if verbosity >= 1:
		print(f"\033[93mERROR: '{tolerance_string}' is not a valid tolerance!\033[0m")
		if verbosity >= 2: print("Tolerance must be a float from 0 to 1.\nSee help (-h or --help) for more info on arguments.")
del tolerance_string

# get min length
try:
	min_length = int(length_string)
	if tolerance < 0: raise ValueError
except ValueError:
	error = True
	if verbosity >= 1:
		print(f"\033[93mERROR: '{length_string}' is not a valid minimum length!\033[0m")
		if verbosity >= 2: print("Length must be a positive integer.\nSee help (-h or --help) for more info on arguments.")
del length_string

# check disposal method
if not (disposal == 'none' or disposal == 'trash' or disposal == 'overwrite'):
	error = True
	if verbosity >= 1:
		print(f"\033[93mERROR: '{disposal}' is not a valid disposal method!\033[0m")
		if verbosity >= 2: print("Valid disposal methods are: none, trash, overwrite.\nSee help (-h or --help) for more info on arguments.")

# check for send2trash
elif disposal == 'trash':
	try: from send2trash import send2trash
	except ModuleNotFoundError:
		error = True
		if verbosity >= 1:
			print("\033[93mERROR: No such module 'send2trash'.\033[0m")
			if verbosity >= 2: print("The python module send2trash is required to use the trash disposal method. Either get send2trash, or use a different disposal method.")

# check mode
if not (mode == 'all' or mode == 'middle' or mode == 'start' or mode == 'end' or mode == 'trim'):
	error = True
	if verbosity >= 1:
		print(f"\033[93mERROR: '{mode}' is not a valid mode!\033[0m")
		if verbosity >= 2: print("Valid modes are: all, middle, start, end, trim.\nSee help (-h or --help) for more info on arguments.")

# check path
if not len(arguments):
	error = True
	if verbosity >= 1:
		print("\033[93mERROR: No path given!\033[0m")
		if verbosity >= 2: print("Please give a path to an audio file or directory.")

# exit if there were errors
if error: exit()
del error


# get audio files

# given file
if os.path.isfile(arguments[0]):
	if what(arguments[0]).filetype == 'wav': files = [arguments[0]]
	# if not a valid audio file file
	else:
		if verbosity >= 1:
			print(f"\033[93mERROR: '{os.path.basename(arguments[0])}' is not a valid audio file!\033[0m")
			if verbosity >= 2: print("This script can only modify wave files. (.wav)")
		exit()

# given directory
elif os.path.isdir(arguments[0]):
	if verbosity >= 3: print("Finding audio files...")
	files = []
	
	def get_audio_files(directory):
		global files
		dir_audio_files = []
		for sub_path in os.listdir(directory):
			path = os.path.join(directory, sub_path)
			if os.path.isfile(path) and what(path).filetype == 'wav':
				if verbosity >= 4: print("Found audio_file", sub_path)
				dir_audio_files.append(path)
			elif recursive and os.path.isdir(path):
				if verbosity >= 4: print("Found directory", os.path.abspath(path))
				get_audio_files(path)
		if verbosity >= 3 and recursive and len(dir_audio_files): print(f"Found {len(dir_audio_files)} audio files in {os.path.abspath(directory)}")
		files += sorted(dir_audio_files)
	
	get_audio_files(arguments[0])
	
	if len(files):
		if verbosity >= 2: print(f"Total of {len(files)} audio files found.")
	else:
		if verbosity >= 1:
			if recursive: print(f"\033[93mNo audio files found in {os.path.abspath(arguments[0])} or any subdirectories.\033[0m")
			else:
				print(f"\033[93mNo audio files found in {os.path.abspath(arguments[0])}.\033[0m")
				if verbosity >= 2: print("Use -r or --recursive to also search subdirectories.")
		exit()

# if given path is not a valid audio file or directory
else:
	if verbosity >= 1: print(f"\033[93mERROR: '{os.path.abspath(arguments[0])}' is not a valid audio file or directory!\033[0m")
	exit()

def print_progress(progress, size=20, show_percent=True, ndigits=1, end='\n'):
	bars = int(min(progress, 1) * size)
	remainder = progress * size - bars
	print('[' + '#' * bars + '-' * (size - bars) + ']', end=' ' if show_percent else end)
	if show_percent:
		percent = round(progress * 100, ndigits)
		print(' ' * ((ndigits + 4 if ndigits else 3) - len(str(percent))), percent, '%', sep='', end=end)

# remove silence
files_modified = 0
total_shrink = 0
for file_path in files:
	
	file_name = os.path.basename(file_path)
	if verbosity >= 4: print(f"\nReading \033[95m{file_name}\033[0m...")
	elif verbosity >= 3: print(f"\033[95m{file_name}\033[0m")
	
	channels = 0
	rate = 0
	frames = []
	# get data
	try:
		if what(arguments[0]).filetype == 'wav':
			with wave.open(file_path) as audio_file:
				channels = audio_file.getnchannels()
				rate = audio_file.getframerate()
				sample_width = audio_file.getsampwidth()
				starting_length = audio_file.getnframes()
				if verbosity >= 3: print(f"File is {starting_length} samples long.")
				# get audio
				audio_data = audio_file.readframes(starting_length)
				
				def frame_value(frame):
					return int.from_bytes(frame, 'little', signed=True) * 2 / 256 ** sample_width
				
				if verbosity >= 3: print("Reading file...")
				last_print = 0
				for frame in range(starting_length):
					frame_data = audio_data[frame * channels * sample_width: (frame + 1) * channels * sample_width]
					if channels == 1: frames.append(frame_value(frame_data))
					elif channels == 2: frames.append([frame_value(frame_data[:sample_width]), frame_value(frame_data[sample_width:])])
					if verbosity >= 3 and time() > last_print + .01:
						print_progress(round(frame / starting_length, 3), end='\r')
						last_print = time()
				if verbosity >= 3: print_progress(1.0)
	except:
		if verbosity >= 1: print(f"\033[93mERROR: '{file_name}' failed to read. Skipping file.\033[0m")
	
	# remove silence
	else:
		def is_silent(frame):
			if channels == 1: return abs(frame) <= tolerance
			elif channels == 2:
				return abs(frame[0]) <= tolerance and abs(frame[1]) <= tolerance
		
		def print_removed(message, start=starting_length):
			removed = start - len(frames)
			print(f"Removed {str(removed)}/{str(start)} ({str(round(removed / start * 100, 2))}%) {message}.")
		
		if mode == 'all' or mode == 'trim' or mode == 'start':
			if verbosity >= 3: print("Trimming start...")
			if is_silent(frames[0]):
				pos = 1
				while is_silent(frames[pos]): pos += 1
				frames = frames[pos:]
				if verbosity >= 3: print_removed("samples from start")
			elif verbosity >= 4: print("No silence found at start.")
		
		if mode == 'all' or mode == 'trim' or mode == 'end':
			if verbosity >= 4: print("Trimming end...")
			if is_silent(frames[-1]):
				pos = -1
				while is_silent(frames[pos - 1]): pos -= 1
				frames = frames[:pos]
				if verbosity >= 3: print_removed("samples from end", len(frames) - pos)
			elif verbosity >= 4: print("No silence found at end.")
		
		if mode == 'all' or mode == 'middle':
			if verbosity >= 4: print("Scanning for silence between sounds...")
			search_pos = 1
			trimmed_length = len(frames)
			
			last_print = 0
			while search_pos < len(frames) - 1:
				if is_silent(frames[search_pos]):
					end_pos = search_pos + 1
					while is_silent(frames[end_pos]): end_pos += 1
					if end_pos - search_pos >= min_length: frames = frames[:search_pos] + frames[end_pos:]
					else: search_pos = end_pos
					if verbosity >= 3 and time() > last_print + .01:
						print_progress(search_pos / len(frames), 20, True, end='\r')
						last_print = time()
				search_pos += 1
			
			if verbosity >= 3:
				print_progress(1.0, 20, True)
				if len(frames) < trimmed_length: print_removed("samples", trimmed_length)
				elif verbosity >= 4: print("No silence found between sounds.")
		
		# save file
		if len(frames) == starting_length:
			if verbosity >= 3: print(f"No silence was found in {file_name}. Skipping saving process.")
			elif verbosity >= 2: print(f"No silence was found in {file_name}.")
		else:
			if verbosity >= 3: print_removed("samples total")
			if verbosity >= 4: print(f"\nSaving changes to {os.path.basename(file_name)}...")
			initial_size = os.path.getsize(file_path)
			try:
				with wave.open(file_path + '.tmp', 'wb') as audio_file:
					audio_file.setnchannels(channels)
					audio_file.setframerate(rate)
					audio_file.setsampwidth(sample_width)
					
					def frame_data(frame):
						return [int(byte) for byte in int(round(frame / 2 * 256 ** sample_width)).to_bytes(sample_width, 'little', signed=True)]
					
					audio_data = []
					last_print = 0
					for frame in frames:
						if channels == 1: audio_data += frame_data(frame)
						elif channels == 2: audio_data += frame_data(frame[0]) + frame_data(frame[1])
						if verbosity >= 3 and time() > last_print + .01:
							print_progress(len(audio_data) / len(frames) / channels / sample_width, 20, True, end='\r')
							last_print = time()
					if verbosity >= 3: print_progress(1.0, 20, True)
					audio_file.writeframes(bytes(audio_data))
			except:
				if verbosity >= 1:
					print(f"\033[93m[ERROR] Failed to save {file_name}!\033[0m Saving aborted. (File has not been modified.)")
			# rename file
			else:
				new_size = os.path.getsize(file_path + '.tmp')
				new_file_path = file_path
				error = False
				if disposal == 'none':
					if '.' in file_name:
						dot_pos = file_path.rfind('.')
						new_file_path = file_path[:dot_pos] + '-unsilenced' + file_path[dot_pos:]
					else: new_file_path += '-unsilenced'
					file_name = os.path.basename(new_file_path)
				elif disposal == 'trash':
					try: send2trash(file_path)
					except OSError:
						error = True
						if verbosity >= 1: print("\033[93m[ERROR] Trashing failed!\033[0m Aborting save.")
				
				if not error:
					os.rename(file_path + '.tmp', new_file_path)
					
					if verbosity >= 2: print(f"{file_name} saved ({initial_size - new_size}B smaller).")
					files_modified += 1
					total_shrink += initial_size - new_size

if len(files) > 1:
	if files_modified: print(f"{files_modified} out of {len(files)} files modified, {total_shrink}B total.")
	else: print("No files were modified.")
