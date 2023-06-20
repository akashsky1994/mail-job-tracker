import os
import csv
import pandas as pd

def append_job_data_archived(data):
    headers = data[0].keys()
    with open('job_application_status.csv', 'a', newline='\n') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    
# Using Pandas    
def append_job_data(data):
    df = pd.DataFrame.from_dict(data)
    output_path='job_application_status.csv'
    df.to_csv('job_application_status.csv', mode='a', header=not os.path.exists(output_path))

def trim_mail_content(content,n_chars):
    # count = 0
    # for i,c in enumerate(content['mail_body']):
    #     if not c.isspace():
    #         count+=1
    #     if count>n_chars:
    #         content['mail_body'] = content['mail_body'][:i]
    if len(content['mail_body'])>n_chars:
        content['mail_body'] = content['mail_body'][:n_chars]
    return content