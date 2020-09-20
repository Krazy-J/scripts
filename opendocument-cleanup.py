#!/usr/bin/python

import sys
sys_arguments = sys.argv
sys_arguments.pop(0)

if len(sys_arguments):
	
	arguments = []
	show_help = False
	remove_fonts = False
	remove_language = True
	overwrite = False
	recursive = False
	verbosity = -1
	
	while len(sys_arguments):
		# "minus minus" argument
		if sys_arguments[0][:1] == "--":
			if sys_arguments[0] == "--help":
				show_help = True
				break
			if sys_arguments[0] == "--removefonts": remove_fonts = True
			if sys_arguments[0] == "--keeplanguage": remove_language = False
			if sys_arguments[0] == "--overwrite": overwrite = True
			if sys_arguments[0] == "--recursive": recursive = True
			if sys_arguments[0] == "--verbosity": verbosity = int(sys_arguments.pop(1))
			sys_arguments.pop(0)
		# "minus" argument
		elif sys_arguments[0][0] == "-":
			if sys_arguments[0] == "-v": verbosity = int(sys_arguments.pop(1))
			else:
				if not sys_arguments[0].find("h") == -1:
					show_help = True
					break
				if not sys_arguments[0].find("f") == -1: remove_fonts = True
				if not sys_arguments[0].find("l") == -1: remove_language = False
				if not sys_arguments[0].find("o") == -1: overwrite = True
				if not sys_arguments[0].find("r") == -1: recursive = True
			sys_arguments.pop(0)
		# other argument
		else:
			arguments.append(sys_arguments.pop(0))
	
	del sys_arguments
	
	
	if show_help:
		print("\n\033[95m──────── OpenDocument Cleanup Usage ────────\033[0m")
		print("This script is used to clean up formatting in OpenDocument Text (.odt) files. By default, this includes unused or redundant information in the content of the document.")
		print("The document cleanup only affects the content of the document, being everything that's on the page. That means styles will remain untouched.")
		print("To cleanup a document, run the script with the path to the document you want to cleanup after the script name. You can also put a path to a folder containing all the documents you want to clean up. By default, cleaned-up documents will be saved as copies. That way, just in case the script does something that messes up a document, you still have the original. It's a good idea to make sure your documents still look right after using the script.")
		print("\n\033[95m──────── Arguments ────────\033[0m")
		print("-h, --help")
		print("	Display this menu. This argument overrides all other operations, regardless of what other arguments are used.")
		print("-f, --removefonts")
		print("	Remove font information (typeface only) from direct formatting information. I highly suggest using this if only one font is used in a given document.")
		print("-l, --keeplanguage")
		print("	Keep language and country information. Not sure what this information is for honestly, but I'm pretty sure it isn't important enough to justify the mess it makes.")
		print("-o, --overwrite")
		print("	Overwrite original documents instead of creating copies.")
		print("	I strongly advise you to only use this if you have some way to revert the change, just in case this script messes something up.")
		print("-r, --recursive")
		print("	Also look in subdirectories when searching for documents in a directory.")
		print("-v, --verbosity <amount, 0-3>")
		print("	Changes the amount of information that is printed during cleanup. This defaults to 4 when a document is given, and 3 when a directory is given.")
		print("	0 -	Nothing (not recommended)")
		print("	1 -	Errors only")
		print("	2 -	+ Opening/saving")
		print("	3 -	+ Data removal stats, individual documents found")
		print("	4 -	All available info and current process updates")
	
	else:
		
		import os
		import zipfile
		
		documents = []
		
		# get documents from path
		def is_document(path):
			if zipfile.is_zipfile(path) and zipfile.Path(path, "content.xml").exists(): return True
			else: return False
		
		if os.path.isfile(arguments[0]) and is_document(arguments[0]):
			if verbosity == -1: verbosity = 4
			documents = [arguments[0]]
		
		elif os.path.isdir(arguments[0]):
			if verbosity == -1: verbosity = 3
			
			def get_documents(directory):
				if verbosity >= 3: print("Finding documents...")
				documents = []
				for sub_path in os.listdir(directory):
					path = os.path.join(directory, sub_path)
					if os.path.isfile(path) and is_document(path):
						if verbosity >= 3: print("Found document", sub_path)
						documents.append(path)
					elif recursive and os.path.isdir(path):
						if verbosity >= 4: print("Found directory", path)
						documents += get_documents(path)
				return documents
				
			
			documents = get_documents(arguments[0])
			
			if len(documents):
				if verbosity >= 2: print("Found", len(documents), "documents.")
			else:
				if verbosity >= 1:
					if recursive: print("\033[93mFailed to find any documents in", arguments[0], "or in any subdirectories.\033[0m")
					else: print("\033[93mFailed to find any documents in", arguments[0] + ".\033[0m")
		
		elif verbosity >= 1 or verbosity == -1: print("\033[93mERROR:", arguments[0], "is not a valid file or directory!\033[0m")
		
		# cleanup documents
		documents_cleaned = 0
		for document in documents:
			document_name = os.path.basename(document)
			
			if verbosity >= 2: print("\nReading \033[95m" + document_name + "\033[0m.")
			content = zipfile.Path(document, "content.xml").read_text()
			
			
			def get_xml_end(xml, search_pos):
				if not xml[search_pos] == '<': search_pos = xml.find('<', 0, search_pos)
				levels = 0
				while True:
					block_end = xml.find('>', search_pos)
					if xml[search_pos + 1] == '/': levels -= 1
					elif not xml[block_end - 1] == '/': levels += 1
					if levels <= 0: return block_end + 1
					search_pos = xml.find('<', search_pos + 1)
			
			
			if verbosity >= 4: print("Beginning content cleanup process...\n")
			
			def get_property(element_pos, name):
				start = content.find(name + '="', element_pos) + len(name) + 2
				return content[start : content.find('"', start)]
			
			def remove_all_elements(elements = []):
				global content
				removed = 0
				while True:
					try:
						search_pos = content.index(elements[0])
						end_pos = search_pos + len(elements[0])
						for element in elements[1:]: end_pos = content.index(element, end_pos) + len(element)
					except:
						return removed
					content = content[0:search_pos] + content[end_pos:]
					removed += 1
			
			
			if verbosity >= 4: print("Taking out the trash...")
			if not content.find(' officeooo:rsid="') == -1:
				removed = remove_all_elements([' officeooo:rsid="', '"'])
				if verbosity >= 3: print("\033[92mRemoved", removed, "officeooo:rsid entries\033[0m")
			if not content.find(' loext:opacity="100%"') == -1:
				removed = remove_all_elements([' loext:opacity="100%"'])
				if verbosity >= 3: print("\033[92mRemoved", removed, "loext:opacity entries\033[0m")
			if remove_fonts:
				if verbosity >= 4: print("Searching for fonts...")
				if not content.find('<style:font-face') == -1:
					removed = remove_all_elements(['<style:font-face', '/>'])
					if verbosity >= 3: print("\033[94mRemoved", removed, "fonts.\033[0m")
				if not content.find(' style:font-name="') == -1:
					removed = remove_all_elements([' style:font-name="', '"'])
					if verbosity >= 3: print("\033[94mRemoved font from", removed, "styles.\033[0m")
			if remove_language:
				if verbosity >= 4: print("Searching for languages and countries...")
				if not content.find('style:language') == -1:
					removed = remove_all_elements([' style:language', '"', '"'])
					if verbosity >= 3: print("\033[92mLanguages removed from direct formatting in", removed, "places.\033[0m")
				if not content.find('style:country') == -1:
					removed = remove_all_elements([' style:country', '"', '"'])
					if verbosity >= 3: print("\033[92mCountries removed from direct formatting in", removed, "places.\033[0m")
			
			if verbosity >= 4: print("Searching for orphan styles...")
			search_pos = 0
			removed = 0
			while True:
				# find style
				try: search_pos = content.index('<style:style', search_pos)
				except: break
				# check to see if it's used anywhere
				try: content.index('style-name="' + get_property(search_pos, 'style:name'))
				# remove style
				except:
					content = content[:search_pos] + content[get_xml_end(content, search_pos):]
					removed += 1
				# next style
				else: search_pos += 1
			if verbosity >= 3 and removed: print("\033[92mRemoved", removed, "orphan styles.\033[0m")
			
			if verbosity >= 4: print("Searching for orphan list styles...")
			search_pos = 0
			removed = 0
			while True:
				# find style
				try: search_pos = content.index('<text:list-style', search_pos)
				except: break
				# check to see if it's used anywhere
				try: content.index('style-name="' + get_property(search_pos, 'style:name'))
				# remove style
				except:
					content = content[:search_pos] + content[get_xml_end(content, search_pos):]
					removed += 1
				# next style
				else: search_pos += 1
			if verbosity >= 3 and removed: print("\033[92mRemoved", removed, "orphan lists styles.\033[0m")
			
			if verbosity >= 4: print("Searching for duplicate styles...")
			search_pos = 0
			removed = 0
			while True:
				# find style
				try: search_pos = content.index('<style:style', search_pos)
				except: break
				# get data in matchable format
				style_data = content[content.find('"', search_pos + 25) : get_xml_end(content, search_pos)]
				# search for matching style
				compare_pos = search_pos + 1
				while True:
					try: compare_pos = content.index('<style:style', compare_pos)
					except: break
					# remove style
					if style_data == content[content.find('"', compare_pos + 25) : get_xml_end(content, compare_pos)]:
						content = content.replace('style-name="' + get_property(compare_pos, 'style:name'), 'style-name="' + get_property(search_pos, 'style:name'))
						content = content[:compare_pos] + content[get_xml_end(content, compare_pos):]
						removed += 1
					# next style
					else: compare_pos += 1
				search_pos += 1
			if verbosity >= 3 and removed: print("\033[92mRemoved", removed, "duplicate styles.\033[0m")
			
			if verbosity >= 4: print("Searching for duplicate list styles...")
			search_pos = 0
			removed = 0
			while True:
				# find style
				try: search_pos = content.index('<text:list-style', search_pos)
				except: break
				# get data in matchable format
				style_data = content[content.find('"', search_pos + 30) : get_xml_end(content, search_pos)]
				# search for matching style
				compare_pos = search_pos + 1
				while True:
					try: compare_pos = content.index('<text:list-style', compare_pos)
					except: break
					# remove style
					if style_data == content[content.find('"', compare_pos + 30) : get_xml_end(content, compare_pos)]:
						content = content.replace('style-name="' + get_property(compare_pos, 'style:name'), 'style-name="' + get_property(search_pos, 'style:name'))
						content = content[:compare_pos] + content[get_xml_end(content, compare_pos):]
						removed += 1
					# next style
					else: compare_pos += 1
				search_pos += 1
			if verbosity >= 3 and removed: print("\033[92mRemoved", removed, "duplicate list styles.\033[0m")
			
			search_pos = 0
			empty = 0
			while True:
				# find style
				try: search_pos = content.index('<style:style', search_pos)
				except: break
				# check properties
				if not content.find('<style:text-properties/>', search_pos, get_xml_end(content, search_pos)) == -1: empty += 1
				search_pos += 1
			if empty:
				if verbosity >= 4: print("Found", empty, "empty styles leftover. LibreOffice will clean these up on it's own when saving the document.")
				elif verbosity >= 3: print("Found", empty, "empty styles leftover.")
			
			if content == zipfile.Path(document, "content.xml").read_text():
				if verbosity >= 2: print("No changes have been made to the document. Skipping saving process.")
			else:
				try:
					with zipfile.ZipFile(document) as doc:
						with zipfile.ZipFile(document + ".cleanup", "w") as temp_doc:
							if verbosity >= 4: print("\nUpdating", document_name, "...")
							temp_doc.writestr("content.xml", content.encode(), compress_type=zipfile.ZIP_DEFLATED)
							for item in doc.infolist():
								if not temp_doc.namelist().count(item.filename):
									temp_doc.writestr(item, doc.read(item.filename))
					documents_cleaned += 1
				except:
					if verbosity >= 1: print("\033[93mSaving failed! Document has not been modified.\033[0m")
				else:
					if overwrite:
						os.remove(document)
						os.rename(document + ".cleanup", document)
					elif document[-4:] == ".odt": os.rename(document + ".cleanup", document.replace(".odt", "-cleaned.odt"))
					elif document[-4:] == ".ott": os.rename(document + ".cleanup", document.replace(".ott", "-cleaned.ott"))
					if verbosity >= 2: print("\033[92m" + document_name, "saved.\033[0m")
		if len(documents): print(documents_cleaned, "out of", len(documents), "documents cleaned.")

else:
	print("\033[95m──────── OpenDocument Cleanup Script ────────\033[0m")
	print("This script is used to clean up OpenDocument Text (.odt) files, because LibreOffice doesn't seem to do any cleanup when saving on it's own.")
	print("To view information on how to use this script, use \"-h\" or \"--help\" after the command used to run it.")
