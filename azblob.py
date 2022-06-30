#!/usr/bin/python3

import argparse
import hashlib
import json
import mimetypes
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import parse_qs

import requests

parser = argparse.ArgumentParser()
parser.add_argument("account", help="Name of Azure storage account")
parser.add_argument("container", help="Name of Azure blob container")
parser.add_argument(
    "--target",
    required=False,
    help="Directory to upload contents from (not including itself)",
)
parser.add_argument(
    "--no-warn",
    required=False,
    action="store_true",
    help="Hide warning message about file deletion",
)
parser.add_argument("--no-cache", action="store_true", help="Ignores the upload cache")
parser.add_argument(
    "--replace",
    action="store_true",
    help="Delete all container files not specified in arguments",
)
args = parser.parse_args()

account_name = args.account
container_name = args.container

if not args.no_warn and args.replace and args.target is not None:
    print(
        f'WARNING: This tool will delete all files in "{account_name}/{container_name}" if they are not included in this command!'
    )
    option = input("Do you wish to continue? (yes/no) ").strip()
    if option != "yes":
        print("Cancelled.")
        exit(0)

home_dir = os.path.expanduser("~")
config_path = os.path.join(home_dir, ".azblobrc")

# Read configuration file containing SAS tokens

config = None
try:
    with open(config_path, "r") as f:
        config = json.load(f)
except FileNotFoundError as e:
    print(e)
    example = {
        "account-name1": {
            "ACCOUNT_SAS?": "?[token]",
            "CONTAINER_SAS?": {
                "container-name1": "?[token]",
                "container-name2": "?[token]",
            },
        }
    }
    print("Example:\n" + json.dumps(example, indent=4))
    exit(1)
except Exception as e:
    print(e)
    exit(1)

# Check for SAS tokens corresponding to given cmd arguments
# (1) check for container SAS token
# (2) check for account SAS token, if no container SAS token

sas_token = None
sas_token_type = None
try:
    sas_token = config[account_name]["CONTAINER_SAS"][container_name]
    sas_token_type = "CONTAINER_SAS"
except KeyError:
    try:
        sas_token = config[account_name]["ACCOUNT_SAS"]
        sas_token_type = "ACCOUNT_SAS"
    except KeyError:
        print("Missing SAS token:", account_name, container_name)
        exit(1)

sas_token_expiry = None
try:
    sas_token_expiry = parse_qs(sas_token)["se"][0].replace("T", " ")
except Exception as e:
    print(e)
    print("Invalid SAS token")
    exit(1)

sas_token = sas_token.lstrip("?")
container_endpoint = f"https://{account_name}.blob.core.windows.net/{container_name}"
mime_guess = mimetypes.MimeTypes().guess_type

# Upload directory files to container


def upload_directory(source_path):
    if not os.path.isdir(source_path):
        print("Must be directory:", source_path)
        exit(1)

    upload_cache = None
    upload_cache_key = hashlib.sha1(
        (account_name + container_name).encode()
    ).hexdigest()
    upload_cache_dir = os.path.join(home_dir, ".cache", "azblob")
    upload_cache_path = os.path.join(upload_cache_dir, upload_cache_key)
    try:
        with open(upload_cache_path, "r") as f:
            upload_cache = json.load(f)
    except FileNotFoundError:
        upload_cache = {}
    except Exception as e:
        print(e)
        print("Could not load cache:", upload_cache_path)
        upload_cache = {}

    uploaded_files = set()
    try:
        old_wd = os.getcwd()
        os.chdir(source_path)
        for fn in os.listdir():
            if os.path.isdir(fn):
                uploaded_files.update(upload_files_recursive(fn, upload_cache))
            else:
                is_ok = upload_file(fn, upload_cache)
                if is_ok:
                    uploaded_files.add(fn)
        os.chdir(old_wd)
    finally:
        if args.replace:
            # Delete all container files not part of current upload batch
            current_container_files = set(file[0] for file in get_container_files()[1:])
            for fn in current_container_files:
                if fn not in uploaded_files:
                    # Delete file
                    delete_container_file(fn)
                    # Remove from cache
                    file_name_hash = hashlib.sha1(fn.encode()).hexdigest()
                    if file_name_hash in upload_cache:
                        del upload_cache[file_name_hash]
        os.makedirs(upload_cache_dir, exist_ok=True)
        with open(upload_cache_path, "w") as f:
            json.dump(upload_cache, f)


def upload_file(source_path, upload_cache):
    try:
        with open(source_path, "rb") as f:
            binary_data = f.read()

        # Check cache
        file_name_hash = hashlib.sha1(source_path.encode()).hexdigest()
        file_content_hash = hashlib.sha1(binary_data).hexdigest()
        if not args.no_cache and file_name_hash in upload_cache:
            if upload_cache[file_name_hash] == file_content_hash:
                print("NO CHANGE:", source_path)
                return True

        content_type = mime_guess(source_path)[0]
        if content_type is None:
            content_type = "application/octet-stream"
        headers = {
            "x-ms-date": datetime.utcnow().strftime(r"%a %b %d %T UTC %Y"),
            "x-ms-version": "2020-06-12",
            "x-ms-blob-type": "BlockBlob",
            "Content-Length": str(len(binary_data)),
            "Content-Type": content_type,
            "Accept": "application/json",
        }
        file_url = f"{container_endpoint}/{source_path}?{sas_token}"
        response = requests.put(file_url, headers=headers, data=binary_data)
        print(f"[{response.status_code}] - UPLOADED:", source_path)

        # Save to cache
        upload_cache[file_name_hash] = file_content_hash

        return True
    except Exception as e:
        print(e)
        print("ERROR: Could not upload file:", source_path)
    return False


def upload_files_recursive(source_path, upload_cache):
    successfully_uploaded_files = []
    for root, subdirs, files in os.walk(source_path):
        for fn in files:
            abs_path = os.path.join(root, fn)
            is_ok = upload_file(abs_path, upload_cache)
            if is_ok:
                successfully_uploaded_files.append(abs_path)
    return successfully_uploaded_files


def delete_container_file(source_path):
    try:
        file_url = f"{container_endpoint}/{source_path}?{sas_token}"
        headers = {
            "x-ms-date": datetime.utcnow().strftime(r"%a %b %d %T UTC %Y"),
            "x-ms-version": "2020-06-12",
        }
        response = requests.delete(file_url, headers=headers)
        print(f"[{response.status_code}] - DELETED:", source_path)
    except Exception as e:
        print(e)
        print("ERROR: Could not delete file:", source_path)


# List files in container


relevant_blob_properties = ["Creation-Time", "Last-Modified", "Content-Type"]


def get_container_files():
    headers = {
        "x-ms-date": datetime.utcnow().strftime(r"%a %b %d %T UTC %Y"),
        "x-ms-version": "2020-06-12",
    }
    container_list_url = f"{container_endpoint}?restype=container&comp=list&{sas_token}"
    response = requests.get(container_list_url, headers=headers)
    response_xml_root = ET.fromstring(response.content)
    files = []
    files.append(("Name",) + tuple(relevant_blob_properties))
    for blob_xml in response_xml_root[0]:
        filename = blob_xml[0].text
        if filename is None:
            continue
        file_metadata = []
        file_metadata.append(filename)
        properties_xml = blob_xml[1]
        for prop in relevant_blob_properties:
            b = properties_xml.find(prop)
            if b is None:
                continue
            value = "" if b.text is None else b.text
            if prop == "Last-Modified" or prop == "Creation-Time":
                ts_dt = datetime.strptime(value, r"%a, %d %b %Y %H:%M:%S %Z")
                ts_dt = ts_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
                value = ts_dt.strftime(r"%Y-%m-%d %H:%M:%S")
            file_metadata.append(value)
        files.append(tuple(file_metadata))
    return files


def pprint_table(table, has_header=False):
    col_width = [max(len(x) for x in col) for col in zip(*table)]
    for line in table:
        line_content = (
            "| "
            + " | ".join("{:{}}".format(x, col_width[i]) for i, x in enumerate(line))
            + " |"
        )
        print(line_content)
        if has_header:
            print("-" * len(line_content))
            has_header = False


# Check if cmd arguments include files to upload
# (YES) start file state sync
# (NO) list files in container

if args.target is not None:
    upload_directory(args.target)
else:
    files = get_container_files()
    print("Account:", account_name)
    print("Container:", container_name)
    print(f"Expiry ({sas_token_type}):", sas_token_expiry)
    print()
    pprint_table(files, has_header=True)
