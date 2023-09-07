import os
import pikepdf
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = "config.txt"

def argument_parser():
    parser = argparse.ArgumentParser(description="Lock or unlock your PDF")
    config = parser.add_mutually_exclusive_group()
    config.add_argument("-f", "--file", help="Use the configuration file", action="store_true")
    config.add_argument("-c", "--command_line", help="Configure the script using the command line", action="store_true")

    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("-l", "--lock", help="Lock your PDF(s) with password", action="store_true")
    selection.add_argument("-u", "--unlock", help="Unlock your PDF(s)", action="store_true")
    args = parser.parse_args()
    return parser, args.lock, args.unlock, args.file, args.command_line

def read_configuration_file(file_name):
    try:
        with open(file_name, "r") as file:
            lines = file.readlines()
            source_folder = lines[0].strip()
            destination_folder = lines[1].strip()
            password = lines[2].strip()
        return source_folder, destination_folder, password
    except FileNotFoundError:
        logger.error(f"Configuration file '{file_name}' not found.")
        return None, None, None

def create_destination_folder(destination_folder):
    try:
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            logger.info(f"Directory '{destination_folder}' created")
        else:
            logger.warning(f"Directory '{destination_folder}' already exists")
    except OSError as e:
        logger.error(f"Error creating directory '{destination_folder}': {str(e)}")

def unlock_PDf(source_folder, destination_folder, password):
    count = 0
    for item in os.scandir(source_folder):
        if item.name.endswith(".pdf"):
            file_name = item.name
            try:
                with pikepdf.open(os.path.join(source_folder, file_name), password=password, allow_overwriting_input=True) as mypdf:
                    mypdf.save(os.path.join(destination_folder, file_name))
                logger.info(f"\"{file_name}\" unlocked")
                count += 1
            except pikepdf.PasswordError:
                logger.error(f"The password failed to open the file: \"{file_name}\"")
    return count

def lock_PDf(source_folder, destination_folder, password):
    count = 0
    for item in os.scandir(source_folder):
        if item.name.endswith(".pdf"):
            file_name = item.name
            with pikepdf.open(os.path.join(source_folder, file_name), allow_overwriting_input=True) as mypdf:
                mypdf.save(os.path.join(destination_folder, file_name), encryption=pikepdf.Encryption(owner=password, user=password))
            logger.info(f"\"{file_name}\" locked")
            count += 1
    return count

def resume_operations(count):
    if count == 0:
        logger.info("No files processed.")
    elif count == 1:
        logger.info("1 file processed.")
    else:
        logger.info(f"{count} files processed.")

def main():
    parser, lock, unlock, file, command_line = argument_parser()
    
    if file:
        source_folder, destination_folder, password = read_configuration_file(CONFIG_FILE)
    elif command_line:
        source_folder = input('Insert source folder name: ')
        destination_folder = input('Insert destination folder folder name: ')
        password = input('Insert password: ')
    else:
        parser.print_help()
        return

    if not source_folder or not destination_folder or not password:
        logger.error("Invalid configuration. Please check the configuration file or command-line inputs.")
        return

    create_destination_folder(destination_folder)

    if unlock:
        count = unlock_PDf(source_folder, destination_folder, password)
    elif lock:
        count = lock_PDf(source_folder, destination_folder, password)
    else:
        parser.print_help()
        return

    resume_operations(count)

if __name__ == "__main__":
    main()
