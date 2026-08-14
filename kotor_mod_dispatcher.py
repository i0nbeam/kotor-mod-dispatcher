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

IGNORED_EXTENSIONS = [".txt", ".rtf", ".doc", ".docx"]

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



def install_override_mod(mod_folder: Path, base_folder: Path, override_folder: Path):

    directories = [path for path in mod_folder.rglob("*") if path.is_dir()]

    # Check if the mod files are NOT within a folder with the same name as the mod archive or with the name "override"
    # This is to check if there are multiple variants/optional features in the mod. User must choose and manually install
    if (len(directories) >= 1 and any(directory.name != mod_folder.name and directory.name.lower() != "override" for directory in directories)):
        print(f"{YELLOW}Multiple folders found.\n{RESET}")
        print(mod_folder.name)
        print_folder_tree(mod_folder)


    else:
        print(mod_folder.name)
        print_folder_tree(mod_folder)
        files = [file for file in mod_folder.rglob("*") if file.is_file()]
        excluded_files = input(f"\nEnter filenames to be excluded (separated by spaces, 'q' to cancel install): ").split()
        print()


        if (len(excluded_files) > 0 and excluded_files[0].lower() == 'q'):
            print(f"{YELLOW}Terminating install.{RESET}\n")
            shutil.rmtree(mod_folder)
            sys.exit(1)


        files = [file for file in files if file.name not in excluded_files]

        for file in files:

            if file.suffix in IGNORED_EXTENSIONS or file.name.startswith("~"):
                continue


            elif file.suffix == ".tlk":
                print(f"Moving {file.name} to base folder...")
                shutil.move(file,base_folder)


            else:
                print(f"Moving {file.name} to {base_folder.name}\\{override_folder.name}...")
                try:
                    shutil.move(file, override_folder)
                except shutil.Error:
                    choice = input(f"{YELLOW}{file.name} already exists. Overwrite? (Y/N): {RESET}")
                    choice = choice.lower()
                    if choice == 'y':
                        file.replace(override_folder / file.name)
                    else:
                        continue
        
        print(f"{GREEN}\nFinished.\n{RESET}")

        

        



def install_mod(mod_folder: Path, base_folder: Path, override_folder: Path, auto_override_install: bool):

    print(f"\nSearching for installer...\n")
    installers = list(mod_folder.rglob("*.exe"))

    # Only keep installers that are not within tslpatchdata/
    if len(installers) > 1:
        installers = [installer for installer in installers if not any(parent.name == "tslpatchdata" for parent in installer.parents)]

    
    if len(installers) == 0:
        print()
        print(f"{YELLOW}No installer found.{RESET}")
        print(f"{YELLOW}Loose-file mod.{RESET}")
        print()
        if auto_override_install:
            install_override_mod(mod_folder,base_folder,override_folder)
        return

        
    
    elif len(installers) == 1:
        installer = installers[0]


    else:
        print(f"{YELLOW}Multiple installers found:{RESET}\n")
        for i, installer in enumerate(installers):
            print(f"    [{i}]: {installer.relative_to(mod_folder.parent)}")

        print()
        while(True):
            choice = input(f"Choose an installer (0 to {len(installers)-1}): ")
            if choice.isdigit():
                if 0 <= int(choice) < len(installers):
                    installer = installers[int(choice)]
                    break
                else:
                    print(f"\n{RED}Invalid choice.{RESET}\n")
            else:
                print(f"\n{RED}Input a number between 0 and {len(installers)-1}.{RESET}\n")


    print(f"{CYAN}Running {installer.name}...{RESET}\n")
    subprocess.run([str(installer)], cwd=installer.parent)
    print(f"{GREEN}Installation complete.{RESET}\n")


        


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
    help="Specify which game the mod is for. Used with --automatic.")

parser.add_argument("-a","--automatic", action="store_true",
                    help="Move files to override folder automatically with option of excluding files. Requires a game to be selected via --game.")


args = parser.parse_args()

archive_name = args.filename
game = args.game
automatic_override_install = args.automatic

base_path = K1_BASE_PATH if game == "K1" else K2_BASE_PATH
override_path = K1_OVERRIDE_PATH if game == "K1" else K2_OVERRIDE_PATH
downloads_path = Path.home() / "Downloads"
archive_path = downloads_path / archive_name


if not archive_path.exists():
    print(f"{RED}Archive not found: {archive_path}{RESET}")
    sys.exit(1)

extract_path = downloads_path / archive_path.stem

if extract_path.exists():
    shutil.rmtree(extract_path)


extract_path.mkdir(parents=True)



print()
print(f"{CYAN}{BOLD}╔══════════════════════════╗{RESET}")
print(f"{CYAN}{BOLD}║   KOTOR Mod Dispatcher   ║{RESET}")
print(f"{CYAN}{BOLD}╚══════════════════════════╝{RESET}")
print()
print(f"{WHITE}Archive:{RESET} {archive_path.name}")
print(f"{WHITE}Extracting to {Path.home() / "Downloads"}\\{archive_path.stem}\\ ...{RESET}")


try:
    extract_archive(archive_path,extract_path)
    install_mod(extract_path,base_path,override_path,automatic_override_install)

except py7zr.exceptions.UnsupportedCompressionMethodError as err:
    print(f"\n{RED}ERROR: {RESET}{YELLOW}{err}{RESET}\n")
    print(f"{YELLOW}This .7z archive uses the BCJ2 filter which is currently unsupported by py7zr. Install this mod without kotor_mod_dispatcher.{RESET}\n")
    shutil.rmtree(extract_path)
    sys.exit(1)

except zipfile.BadZipFile as err:
    print(f"\n{RED}ERROR: {RESET}{archive_path.name} is BadZipFile\n")
    print(f"{err}\n")
    print(f"{YELLOW}Try recompressing this archive or install this mod without kotor_mod_dispatcher.{RESET}\n")
    shutil.rmtree(extract_path)
    sys.exit(1)



    








    





