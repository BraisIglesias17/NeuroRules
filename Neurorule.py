import sys, subprocess


if sys.platform.startswith('linux'):
    subprocess.run("GTK_THEME=Adwaita:light python main.py", shell=True)
else:
    subprocess.run("python main.py", shell=True)


    
