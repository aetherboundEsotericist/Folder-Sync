import shutil
import filecmp
import os
import argparse
import sys
import logging
import schedule
import time



#Collect command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", help= "Source folder. Must be a valid path.", required=True)
parser.add_argument("-d", "--destination", help= "Destination folder. Must be a valid path.", required=True)
parser.add_argument("-l", "--log", help= "Folder where the log file will be created. Must be a valid path..", required=True)
parser.add_argument("-i", "--interval", help= "How often, in seconds, synchronization should occur. Must be an integer.", required=True)

args = parser.parse_args()

#Ensures all arguments are valid
if not os.path.exists(args.source): sys.exit("Provided Source path is invalid. Make sure the path exists. If the provided path contains spacebar characters, encase the path in quotes.")
if not os.path.exists(args.destination): sys.exit("Provided Destination path is invalid. Make sure the path exists. If the provided path contains spacebar characters, encase the path in quotes.")
if not os.path.exists(args.log): sys.exit("Provided Log Folder path is invalid. Make sure the path exists. If the provided path contains spacebar characters, encase the path in quotes.")
if not args.interval.isdigit(): sys.exit("Provided Interval is invalid. Make sure it's an integer.")

inputSrcFolderPath = args.source
inputDstFolderPath = args.destination
inputInterval = int(args.interval)

#Create the log file if it doesn't exist
logFilePath = os.path.join(args.log, "history.log")
open(logFilePath, "a")


#Create the logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename=logFilePath, level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

#Define functions
def print_and_log(message):
    print(message)
    logger.info(message)



def copy_item(srcPath, dstPath, item):
    srcItemPath = os.path.join(srcPath, item)
    newItemPath = os.path.join(dstPath, item)

    #shutil has separate functions for files and directories
    if os.path.isdir(srcItemPath):
        print("\ndirectory %s exists only in Source" %(item))
        shutil.copytree(srcItemPath, newItemPath)
        print_and_log("created folder: " + newItemPath)
    else:
        print("\nfile %s exists only in Source" %(item))
        shutil.copy(srcItemPath, dstPath)
        print_and_log("created file: " + newItemPath)
        


def delete_item(itemPath):
    #Uses shutil to delete directories or an OS function to delete files
    if os.path.isdir(itemPath):
        shutil.rmtree(itemPath)
        print_and_log("deleted folder: " + itemPath)
    else:
        os.remove(itemPath)
        print_and_log("deleted file: " + itemPath)



def overwrite_file(srcPath, dstPath, file):
        srcFilePath = os.path.join(srcPath, file)
        dstFilePath = os.path.join(dstPath, file)
        print_and_log("overwriting " + dstFilePath)
        os.remove(dstFilePath)
        shutil.copy(srcFilePath, dstPath)



def sync_folders(srcFolderPath, dstFolderPath):
    comparationClass = filecmp.dircmp(srcFolderPath, dstFolderPath, shallow=False)

    #Copy items (files and directories) that exist only in the Source folder
    for item in comparationClass.left_only:
        copy_item(srcFolderPath, dstFolderPath, item)
        
    #Delete items that exist only in the Destination folder
    for item in comparationClass.right_only:
        print("\nitem %s exists only in Destination" %(item))
        itemPath = os.path.join(dstFolderPath, item)
        delete_item(itemPath)

    #Overwrite files (but not directories) that exist in both directories but differ in content. Files are deleted from the Destination and copied over from the Source
    for file in comparationClass.diff_files:
        print("\nfile %s differs from Source to Destination" %(file))
        overwrite_file(srcFolderPath, dstFolderPath, file)

    #Access directories and run the same logic recursively
    for folder in comparationClass.subdirs:
        nextSrcFolderPath = os.path.join(srcFolderPath, folder)
        nextDstFolderPath = os.path.join(dstFolderPath, folder)
        sync_folders(nextSrcFolderPath, nextDstFolderPath)



#Run the program
print_and_log("program started")

def job(): sync_folders(inputSrcFolderPath, inputDstFolderPath)

schedule.every(inputInterval).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)