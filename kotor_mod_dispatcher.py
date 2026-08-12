import sys
import py7zr
import rarfile
import zipfile
import subprocess
import shutil
from pathlib import Path
import colorama

GREEN = colorama.Fore.GREEN      
YELLOW = colorama.Fore.YELLOW     
RED = colorama.Fore.RED          
CYAN = colorama.Fore.CYAN         
WHITE = colorama.Fore.WHITE       
RESET = colorama.Style.RESET_ALL
BOLD = colorama.Style.BRIGHT

#-----------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------


def print_folder_tree(path: Path, prefix=""):
    entries = sorted(
        path.iterdir(),
        key=lambda p: (p.is_file(), p.name.lower())
    )

    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "

        print(prefix + connector + entry.name)

        if entry.is_dir():
            extension = "    " if is_last else "│   "
            print_folder_tree(entry, prefix + extension)



def extract_archive(archive_path: Path,extract_path: Path):


    extension = archive_path.suffix.lower()

    if extension == ".7z":
        with py7zr.SevenZipFile(archive_path, mode='r') as archive:
            archive.extractall(path=extract_path)
    elif extension == ".rar":
        with rarfile.RarFile(archive_path) as archive:
            archive.extractall(path=extract_path)

    elif extension == ".zip":
        with zipfile.ZipFile(archive_path, "r") as archive:
            archive.extractall(extract_path)

    else:
        print(f"{RED}Unsupported archive type: {extension}{RESET}")
        sys.exit(1)

    print(extracted_path.name)
    print_folder_tree(extracted_path)
    print()
    print(f"{GREEN}Extracting complete.{RESET}")



def install_mod(extract_path: Path):

    print(f"\nSearching for installer...")
    installers = list(extract_path.rglob("*.exe"))

    if len(installers) == 0:
        print()
        print(f"{YELLOW}No installer found.{RESET}")
        print(f"{YELLOW}Loose-file mod.{RESET}")
        print()
        return
    
    elif len(installers) == 1:
        installer = installers[0]


    else:
        print(f"{YELLOW}Multiple installers found:{RESET}")

        for i, installer in enumerate(installers):
            print(f"    [{i}]: {installer}")

        while(True):
            choice = int(input(f"{CYAN}Choose an installer:{RESET}"))
            if 0 <= choice < len(installers):
                installer = installers[choice]
                break
            else:
                print(f"{RED}Invalid choice.{RESET}\n")


    print(f"\n{CYAN}Running {installer.name}...{RESET}")
    subprocess.run([str(installer)], cwd=installer.parent)
    print(f"\n{GREEN}Installation complete.{RESET}")
    print(f"\nDeleting {extract_path}\\ ...\n")
    shutil.rmtree(extract_path)

        


#-----------------------------------------------------------------------
# Script start
#-----------------------------------------------------------------------


colorama.init() # init pretty colors

if len(sys.argv) != 2:
    print(f"{YELLOW}Usage: python kotor_modinstall.py [mod_name.zip/rar/7z]{RESET}")
    print(f"{YELLOW}Example: python kotor_modinstall.py mod.zip{RESET}")
    sys.exit(1)


archive_name = sys.argv[1]

downloads_path = Path.home() / "Downloads"
archive_path = downloads_path / archive_name


if not archive_path.exists():
    print(f"{RED}Archive not found: {archive_path}{RESET}")
    sys.exit(1)

extracted_path = downloads_path / archive_path.stem

if extracted_path.exists():
    shutil.rmtree(extracted_path)


extracted_path.mkdir(parents=True)



print()
print(f"{CYAN}{BOLD}╔══════════════════════════╗{RESET}")
print(f"{CYAN}{BOLD}║   KOTOR Mod Dispatcher   ║{RESET}")
print(f"{CYAN}{BOLD}╚══════════════════════════╝{RESET}")
print()
print(f"{WHITE}Archive:{RESET} {archive_path.name}")
print(f"{WHITE}Extracting to {Path.home() / "Downloads"}\\{archive_path.stem}\\ ...{RESET}")



extract_archive(archive_path,extracted_path)


install_mod(extracted_path)






    





