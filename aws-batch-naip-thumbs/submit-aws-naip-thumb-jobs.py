import json
import boto3

batch = boto3.client('batch')
s3 = boto3.client('s3')


states = s3.list_objects(Bucket='aws-naip', 
      Delimiter="/", 
      RequestPayer="requester")
      
for state_prefix in states['CommonPrefixes']:
  if state_prefix['Prefix'] == ".misc/":
    continue
    
  years = s3.list_objects(Bucket='aws-naip', 
      Prefix="{0}".format(state_prefix['Prefix']), 
      Delimiter="/", 
      RequestPayer="requester")
  
  if 'CommonPrefixes' not in years:
    continue
  
  for year_prefix in years['CommonPrefixes']:
    input_prefix = year_prefix['Prefix']
    jobName = "NAIP_{0}".format(input_prefix.replace("/", "_"))
    print(jobName)
    
    try:
      response = batch.submit_job(jobQueue='vg-naip-thumbs', 
        jobName=jobName, 
        jobDefinition='vg-aws-naip-thumbs',
        parameters={"input_prefix":input_prefix })
        
      print ("Response: " + json.dumps(response, indent=2))
    except Exception as e:
      print ("Error submitting Batch Job")
      print (e)
