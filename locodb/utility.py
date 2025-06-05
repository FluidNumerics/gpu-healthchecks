# Miscellanous utilities

from datetime import datetime, timezone
import os
import urllib.request
import xml.etree.ElementTree as ET
import pytz


def iso_to_local_datetime(iso_string):
    """Converts an ISO 8601 string to a datetime object in local time.

    Args:
        iso_string: The ISO 8601 formatted string.

    Returns:
        A datetime object representing the local time, or None if an error occurs.
    """
    try:
        # Parse the ISO string to a datetime object
        dt_object = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))

        # If the datetime object is naive, assume UTC
        if dt_object.tzinfo is None or dt_object.tzinfo.utcoffset(dt_object) is None:
            dt_object = dt_object.replace(tzinfo=pytz.utc)

        # Convert to local time
        local_dt = dt_object.astimezone(
            pytz.utc
        )  # Replace pytz.utc with your local timezone if needed

        return local_dt
    except ValueError:
        return None


def remove_slash(slash_str: str):
    if "/" in slash_str:
        return slash_str.replace("/", "_")
    else:
        return slash_str


def find_lines_with_char(text, char):
    lines = text.splitlines()
    line_numbers = []
    for i, line in enumerate(lines):
        if char in line:
            line_numbers.append(i + 1)  # Line numbers start from 1
    return line_numbers


def get_timestamp():
    utc_now = datetime.now(timezone.utc)
    timestamp = utc_now.strftime("%Y-%m-%d %H:%M:%S %Z")
    return timestamp


def get_supported_repos(default_xml_path="default.xml"):
    """
    Get the list of supported repositories from the default.xml file.
    """

    if not os.path.exists("default.xml"):
        url = "https://raw.githubusercontent.com/ROCm/ROCm/develop/default.xml"
        urllib.request.urlretrieve(url, "default.xml")

    supported_repos = ["ROCm"]
    tree = ET.parse(default_xml_path)
    root = tree.getroot()

    for project in root.findall("project"):
        repo = project.get("name")
        if repo:
            supported_repos.append(repo)

    return supported_repos
