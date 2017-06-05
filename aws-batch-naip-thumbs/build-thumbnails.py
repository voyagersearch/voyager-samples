#!/usr/bin/python
# -*- coding: utf-8 -*-

import boto3
import botocore
import argparse
import os
import os.path
import subprocess
import shutil
import sys

ap = argparse.ArgumentParser()
ap.add_argument('input_bucket', help='Name of bucket that contains input image')
ap.add_argument('input_prefix', help='Prefix to query images')
ap.add_argument('output_bucket', help='Name of bucket to store output thumbnail image')
args = ap.parse_args()

s3 = boto3.client('s3')

paginator = s3.get_paginator('list_objects')
pages = paginator.paginate(Bucket=args.input_bucket, Prefix=args.input_prefix, RequestPayer='requester')
objects = pages.search("Contents[?ends_with(Key, '.tif')][]")

objects_to_process = list()
index = 1
for o in objects:
  sys.stdout.write("Checking {0}\n".format(o['Key']))
  sys.stdout.flush()
  thumb_key_name = o['Key'].replace(".tif", ".thumb.jpg")
  try:
    boto3.resource('s3').Object(args.output_bucket, thumb_key_name).load()
    sys.stdout.write("Skipping {0}\n".format(o['Key']))
    sys.stdout.flush()
    continue
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
      object_to_process = dict()
      object_to_process['Index'] = index
      object_to_process['Key'] = o['Key']
      object_to_process['Bucket'] = args.input_bucket
      objects_to_process.append(object_to_process)
      index = index + 1
    else:
      raise

total = len(objects_to_process)
for object_to_process in objects_to_process:
  try:
    sys.stdout.write("Building thumbnail {0} of {1}: {2}\n".format(object_to_process['Index'], total, object_to_process['Key']))
    sys.stdout.flush()
    os.makedirs(os.path.join('data/input', os.path.dirname(object_to_process['Key'])))
    os.makedirs(os.path.join('data/output', os.path.dirname(object_to_process['Key'])))
  
    thumb_key_name = object_to_process['Key'].replace(".tif", ".thumb.jpg")
  
    s3.download_file(args.input_bucket, object_to_process['Key'], os.path.join('data/input', object_to_process['Key']), ExtraArgs={'RequestPayer':'requester'})

    gdal_translate_cmd_line = ["gdal_translate", "-of", "JPEG", "-ot", "Byte", "-outsize", "270", "270"]
    #gdal_translate_cmd_line.extend(["-scale", "0", "65535", "0", "255"])
    gdal_translate_cmd_line.extend(["--config", "CPL_VSIL_CURL_USE_HEAD", "NO"])
    gdal_translate_cmd_line.extend(["--config", "GDAL_PAM_ENABLED", "NO"])
    gdal_translate_cmd_line.extend(["--config", "GDAL_DISABLE_READDIR_ON_OPEN","TRUE"])
    gdal_translate_cmd_line.extend(["--config", "GDAL_HTTP_UNSAFESSL","YES"])
    #gdal_translate_cmd_line.extend(["--config", "CPL_CURL_VERBOSE", "TRUE"])
    #gdal_translate_cmd_line.extend(["--config", "CPL_DEBUG", "ON"])

    #gdal_translate_cmd_line.append(input_image_url)
    gdal_translate_cmd_line.append(os.path.join('data/input', object_to_process['Key']))
    gdal_translate_cmd_line.append(os.path.join('data/output', thumb_key_name))

    return_code = subprocess.call(gdal_translate_cmd_line)
  
    if return_code != 0:
      continue
  
    boto3.resource('s3').Object(args.output_bucket, thumb_key_name).upload_file(os.path.join('data/output', thumb_key_name))
  
    shutil.rmtree('data/input')
    shutil.rmtree('data/output')
  except Exception as e:
    sys.stdout.write("ERROR. Processing {0} of {1}: {2}\n".format(object_to_process['Index'], total, object_to_process['Key']))
    sys.stdout.write("{0}\n".format(str(e)))
    sys.stdout.flush()
    continue

  