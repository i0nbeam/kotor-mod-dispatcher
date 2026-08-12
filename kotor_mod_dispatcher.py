import sys
import py7zr
import rarfile
import zipfile
import subprocess
import shutil
from pathlib import Path
import colorama
import argparse

#-----------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------

GREEN = colorama.Fore.GREEN      
YELLOW = colorama.Fore.YELLOW     
RED = colorama.Fore.RED          
CYAN = colorama.Fore.CYAN         
WHITE = colorama.Fore.WHITE       
RESET = colorama.Style.RESET_ALL
BOLD = colorama.Style.BRIGHT

K1_BASE_PATH = Path("C:/Program Files (x86)/Steam/steamapps/common/swkotor")
K1_OVERRIDE_PATH = K1_BASE_PATH / "Override"
K2_BASE_PATH = Path("C:/Program Files (x86)/Steam/steamapps/common/Knights of the Old Republic II")
K2_OVERRIDE_PATH = K2_BASE_PATH / "override"

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



def extract_archive(archive_path: Path,mod_folder: Path):

    extension = archive_path.suffix.lower()

    if extension == ".7z":
        with py7zr.SevenZipFile(archive_path, mode='r') as archive:
            archive.extractall(path=mod_folder)
    elif extension == ".rar":
        with rarfile.RarFile(archive_path) as archive:
            archive.extractall(path=mod_folder)

    elif extension == ".zip":
        with zipfile.ZipFile(archive_path, "r") as archive:
            archive.extractall(mod_folder)

    else:
        print(f"{RED}Unsupported archive type: {extension}{RESET}")
        sys.exit(1)

    print()
    print(f"{GREEN}Extracting complete.{RESET}")



def install_override_mod(mod_folder: Path, override_path: Path):

    directories = [path for path in mod_folder.iterdir() if path.is_dir()]

    if (len(directories) >= 0 and all(directory.name == mod_folder.name for directory in directories)):

        print(extracted_path.name)
        print_folder_tree(mod_folder)
        files = [file for file in mod_folder.iterdir() if not file.is_dir()]
        excluded_files = input(f"\nEnter filenames to be excluded (separated by spaces, 'q' to cancel install): ").split()
        print()

        if (len(excluded_files) > 0 and excluded_files[0].lower() == 'q'):
            print(f"{YELLOW}Terminating install.{RESET}\n")
            shutil.rmtree(mod_folder)
            sys.exit(1)

        files = [file for file in files if file not in excluded_files]

        for file in files:

            if file.suffix == ".tlk":
                print(f"Moving {file.name} to base folder...")
                shutil.move(file,K1_BASE_PATH)

            elif file.suffix == ".txt":
                continue

            else:
                print(f"Moving {file.name} to {override_path.parent}/{"override" if game=="K1" else "Override"}...")
                shutil.move(file, K1_OVERRIDE_PATH)

        print(f"{GREEN}Finished.\n{RESET}")

        
    else:
        print(f"{YELLOW}Multiple folders found.\n{RESET}")
        print(extracted_path.name)
        print_folder_tree(mod_folder)

        



def install_mod(mod_folder: Path, auto_override_install: bool):

    print(f"\nSearching for installer...")
    installers = list(mod_folder.rglob("*.exe"))

    if len(installers) == 0:
        print()
        print(f"{YELLOW}No installer found.{RESET}")
        print(f"{YELLOW}Loose-file mod.{RESET}")
        print()
        if auto_override_install:
            install_override_mod(mod_folder,override_path)
        return

        
    
    elif len(installers) == 1:
        installer = installers[0]


    else:
        print(f"{YELLOW}Multiple installers found:{RESET}")

        for i, installer in enumerate(installers):
            print(f"    [{i}]: {installer}")

        while(True):
            choice = input(f"{CYAN}Choose an installer (0 to {len(installers)}):{RESET} ")
            if choice.isdigit():
                if 0 <= choice < len(installers):
                    installer = installers[int(choice)]
                    break
                else:
                    print(f"{RED}Invalid choice.{RESET}\n")
            else:
                print(f"{RED}Input a number between 0 < {len(installers)}{RESET}\n")


    print(f"\n{CYAN}Running {installer.name}...{RESET}")
    subprocess.run([str(installer)], cwd=installer.parent)
    print(f"\n{GREEN}Installation complete.{RESET}")
    print(f"\nDeleting {mod_folder}\\ ...\n")
    shutil.rmtree(mod_folder)


        


#-----------------------------------------------------------------------
# Script start
#-----------------------------------------------------------------------


colorama.init() # init pretty colors

parser = argparse.ArgumentParser(description=f"Mod dispatcher for the KOTOR games.")
parser.add_argument("filename", type=str, help="The mod .zip/.7z/.rar archive.")
parser.add_argument(
    "-g","--game",
    default="K1",
    choices=["K1","K2"],
    type=str,
    help="Specify which game the mod is for. Used when automatically installing into override.")

parser.add_argument("--automatic", action="store_true",
                    help="Move files to override folder automatically with option of excluding certain files")


args = parser.parse_args()

archive_name = args.filename
game = args.game
automatic_override_install = args.automatic


override_path = K1_OVERRIDE_PATH if game == "K1" else K2_OVERRIDE_PATH
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


install_mod(extracted_path,automatic_override_install)






    





