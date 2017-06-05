import sys
import json


def run(entry):
    """
    Python step to compute the Thumb URL for a NAIP on AWS record. Thumbs are located in a
    publicly accessible AWS bucket. Thumbs have the same key as the full resolution image only
    ending in .thumb.jpg instead of .tif
    :param entry: a JSON file containing a voyager entry.
    """
    new_entry = json.load(open(entry, "rb"))
    key = new_entry['entry']['fields']['fs_key']
    thumb_key = key.replace(".tif", ".thumb.jpg")
    thumb_url = "https://voyager-aws-naip.s3.amazonaws.com/{0}".format(thumb_key)
    new_entry['entry']['fields']['image_url'] = thumb_url
    
    sys.stdout.write(json.dumps(new_entry))
    sys.stdout.flush()