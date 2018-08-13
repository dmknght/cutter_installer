#!/usr/bin/env python
"""
	Radare2 Cutter installer
	Tested on Debian 9 + python2
	Does not work with python3
"""


import re, urllib, sys, os

release_url = "https://github.com/radareorg/cutter/releases"
git_server = "https://github.com"
default_path = "/usr/bin/cutter"
desktop_path = "/usr/share/applications/cutter.desktop"

def desktop_shortcut():
	return """[Desktop Entry]
Name=cutter
GenericName=Radare2 Cutter GUI
Comment=Cutter Dissembler
Exec=cutter
Terminal=false
Type=Application
Categories=Qt;Debugger;Dissembler;Cutter
Keywords=debugger;graphical;cutter
"""

def print_version(production, version):
	print("\033[92m%s\033[00m: \033[91m%s\033[00m" %(production, version))

def get_latest_release(extension = ".AppImage"):
	"""
		Get latest release version of Cutter
		Latest version should be on the top of the list
	"""

	regex_link = r"href=\"(.*)%s" %(extension)

	response = urllib.urlopen(release_url).read()


	release_file = re.findall(
		regex_link,
		response,
		re.MULTILINE)[0]

	return "%s%s" %(release_file, extension)

def check_update():
	"""
		1. Check version on server
		2. Check version in current system
		3. If current_versin < server_version:
			call do_update()
	"""

	# 1. Check update
	try:
		print("Connecting to %s" %(release_url))
		latest_release = get_latest_release()
		latest_version = re.findall(r"Cutter-v(.*)-", 
			latest_release,
			re.MULTILINE
		)[0]

		print_version("\tLatest version", latest_version)

	except Exception as error:
		print("Error while connecting to server!")
		sys.exit(error)
	# End of check update

	# 2. Check local_version
	try:
		print("Checking local Cutter version")
		cutter_path = os.popen("whereis cutter | awk '{print $2}'").read().replace("\n", "")

		if cutter_path:
			cutter_version = os.popen("cutter -v 2>/dev/null | awk '{print $2}'").read().replace("\n", "")
			print_version("\tInstallation path", cutter_path)
			print_version("\tLocal version", cutter_version)
		else:
			sys.exit("Can not find cutter!")

	except Exception as error:
		print("Error while checking local version! Reason: ")
		sys.exit(error)

	# End of check local_version
	
	# 3. Do update
	try:
		do_update(cutter_version, latest_version, cutter_path, latest_release)
	except Exception as error:
		print("Error while updating binary file! Reason: ")
		sys.exit(error)

def do_update(local_version, server_version, install_path, update_url):

	if local_version == server_version:
		print_version("\nYour Cutter is up to date", server_version)

	elif local_version < server_version:
		print("Updating cutter")

		download_url = "%s%s" %(git_server, update_url)

		system_install(download_url, install_path)

		print("Update completed")

	else:
		sys.exit("Unknow error")

def system_install(download_url, install_path):
	print_version("\tDownload URL", download_url)
	print_version("\tLocal path", install_path)

	urllib.urlretrieve(download_url, install_path)

def do_install():
	try:
		check_path = os.popen("whereis cutter | awk '{print $2}'").read()
		if check_path.replace("\n", ""):
		# Current system is having cutter, replace it [?]
			try:
				print("\033[91mFound Cutter in your system!\n%s\033[00m" %(check_path))
				choose = raw_input("Install Cutter anyway? [Y]")
				if choose != "y" or choose != "Y":
					print("Canceled [by user]")
					sys.exit(0)
			except KeyboardInterrupt:
				print("Terminated [by user]")
	
		download_url = "%s%s" %(git_server, get_latest_release())
		system_install(download_url, default_path)
		os.popen("chmod 755 %s" %(default_path))
		open(desktop_path, 'w').write(desktop_shortcut())
		print("Installation completed")


	except Exception as error:
		print("Error while installing Cutter! Reason: ")
		sys.exit(error)


def help():
	print("""\t\tRadare2 Cutter Installer Script\n
	\rRequires: python2
	\rThis script must be run as root\n
	\rUsage:
	\r %s\thelp\t\tShow help banner
	\r %s\tinstall\t\tInstall Cutter to your system
	\r %s\tupdate\t\tUpdate your Cutter
	""" %(sys.argv[0], sys.argv[0], sys.argv[0]))

if __name__ == "__main__":
	if len(sys.argv) == 2:
		if sys.argv[1] == "install":
			do_install()
		elif sys.argv[1] == "update":
			check_update()
		elif sys.argv[1] == "help":
			help()
		else:
			print("Unknow command! Use help for more information.")
	else:
		help()
