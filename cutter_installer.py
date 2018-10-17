#!/usr/bin/env python
"""
	Radare2 Cutter installer
	Tested on Debian 9 + python2
	Does not work with python3
"""


import re, urllib, sys, os

REALEASE_URL = "https://github.com/radareorg/cutter/releases"
GIT_SERVER = "https://github.com"
DEFAULT_PATH = "/usr/local/bin/cutter"
DESKTOP_PATH = "/usr/share/applications/cutter.desktop"

def create_appdata():
	return """<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop">
  <id>Cutter.desktop</id>
  <metadata_license>CC0-1.0</metadata_license>
  <project_license>GPL-3.0</project_license>
  <name>Cutter</name>
  <summary>A Qt and C++ GUI for radare2 reverse engineering framework</summary>
  <description>
    <p>
      Cutter is Qt and C++ GUI for radare2, originally named Iaito. It is not aimed at existing radare2 users, but focuses on those whose aren’t fluent yet with the command line, likely because of the steep learning curve.
    </p>
  </description>
  <screenshots>
    <screenshot>
      <image>https://raw.githubusercontent.com/radareorg/cutter/master/docs/screenshot.png</image>
      <caption>Main UI</caption>
    </screenshot>
    <screenshot>
      <image>http://beta.rada.re/en/latest/_images/cutter.png</image>
      <caption>Light Theme</caption>
    </screenshot>
    <screenshot>
      <image>http://beta.rada.re/en/latest/_images/cutter_dark.jpg</image>
      <caption>Dark Theme</caption>
    </screenshot>
  </screenshots>
  <url type="homepage">http://beta.rada.re/en/latest/cutter.html</url>
  <releases>
    <release version="1.7.2" date="2018-10-07" />
    <release version="1.7.1" date="2018-08-25" />
    <release version="1.7" date="2018-08-17" />
    <release version="1.6" date="2018-07-13" />
    <release version="1.5" date="2018-07-02" />
    <release version="1.4" date="2018-04-24" />
    <release version="1.3" date="2018-03-09" />
    <release version="1.2" date="2018-01-30" />
    <release version="1.1" date="2017-12-25" />
    <release version="1.0" date="2017-12-03" />
  </releases>
</component>
"""

def desktop_shortcut():
	return """[Desktop Entry]
	Type=Application
	Name=cutter
	Exec=cutter
	Icon=cutter
	Categories=Development;Disassembler;Debugger;Reversing;cutter;Cutter;
	""".replace("\t", "")

def printf(production, version):
	print("\033[92m%s\033[00m: \033[91m%s\033[00m" %(production, version))

def get_latest_release(extension = ".AppImage"):
	"""
		Get latest release version of Cutter
		Latest version should be on the top of the list
	"""

	regex_link = r"href=\"(.*)%s" %(extension)

	response = urllib.urlopen(REALEASE_URL).read()


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
		print("Connecting to %s" %(REALEASE_URL))
		latest_release = get_latest_release()
		latest_version = re.findall(r"Cutter-v(.*)-",
			latest_release,
			re.MULTILINE
		)[0]

		printf("\tLatest version", latest_version)

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
			printf("\tInstallation path", cutter_path)
			printf("\tLocal version", cutter_version)
		else:
			sys.exit("Can not find Cutter! Install it first?")

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
		printf("\nYour Cutter is up to date", server_version)

	elif local_version < server_version:
		print("Updating cutter")

		download_url = "%s%s" %(GIT_SERVER, update_url)

		system_install(download_url, install_path)

		print("Update completed")

	else:
		sys.exit("Unknow error")

def system_install(download_url, install_path):
	printf("\tDownload URL", download_url)
	printf("\tLocal path", install_path)

	urllib.urlretrieve(download_url, install_path)

def do_install():
	try:
		check_path = os.popen("whereis cutter | awk '{print $2}'").read()
		if check_path.replace("\n", ""):
		# Current system is having cutter, replace it [?]
			try:
				print("\033[91mFound Cutter in your system!\n%s\033[00m" %(check_path))
				choose = raw_input("Install Cutter anyway? [Y]")
				if choose != "y" and choose != "Y":
					print("Canceled [by user]")
					sys.exit(0)
			except KeyboardInterrupt:
				print("Terminated [by user]")

		download_url = "%s%s" %(GIT_SERVER, get_latest_release())
		print("Downloading Cutter to your system")
		system_install(download_url, DEFAULT_PATH)
		print("Setting permission")
		os.popen("chmod 755 %s" %(DEFAULT_PATH))
		check_path = os.popen("whereis cutter | awk '{print $2}'").read() # Fix if check_path is None
		print("\t\033[91m%s\033[00m" %(os.popen("ls -la %s" %(check_path)).read().replace("\n", "")))
		print("Creating .desktop shortcut file")
		printf("\tDesktop shortcut", DESKTOP_PATH)
		open(DESKTOP_PATH, 'w').write(desktop_shortcut())
		printf("Adding image icon")
		os.popen("cp cutter.svg /usr/share/pixmaps/cutter.svg")
		printf("Writing appdata information")
		open("/usr/share/appdata/Cutter.appdata.xml", "w").write(create_appdata())
		print("Installation completed")


	except Exception as error:
		print("Error while installing Cutter! Reason: ")
		sys.exit(error)


def do_help():
	# Usage advanced format string
	# https://stackoverflow.com/a/1225648
	print("""\t\tRadare2 Cutter Installer Script\n
		\r\rRequires: python2
		\r\rThis script must be run as root\n
		\r\rUsage:
		\r\r %(SYSPATH)s\thelp\t\tShow help banner
		\r\r %(SYSPATH)s\tinstall\t\tInstall Cutter to your system
		\r\r %(SYSPATH)s\tupdate\t\tUpdate your Cutter
		\r\r %(SYSPATH)s\tuninstall\tUninstall Cutter"""
	%{'SYSPATH': sys.argv[0]})

def do_uninstall():
	INSTALLED_PATH = os.popen("whereis cutter | awk '{print $2}'").read().replace("\n", "")
	if INSTALLED_PATH:
		try:
			os.remove(INSTALLED_PATH)
			printf("Cutter is removed", INSTALLED_PATH)
			os.remove(DESKTOP_PATH)
			printf("Desktop shortcut is removed", DESKTOP_PATH)
		except Exception as err:
			printf("Error while removing Cutter! Reason:")
			sys.exit(err)
	else:
		printf("Uninstallation canceled", "Cutter not found!")

if __name__ == "__main__":
	if len(sys.argv) == 2:
		if sys.argv[1] == "install":
			do_install()
		elif sys.argv[1] == "update":
			check_update()
		elif sys.argv[1] == "help":
			do_help()
		elif sys.argv[1] == "uninstall":
			do_uninstall()
		else:
			print("Unknow command! Use help for more information.")
	else:
		do_help()
