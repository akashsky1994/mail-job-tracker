import os
import csv
import pandas as pd

def append_job_data_archived(data, file_path='job_application_status.csv'):
    headers = data[0].keys()
    with open(file_path, 'a', newline='\n') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    
# Using Pandas    
def append_job_data(data, file_path='job_application_status.csv'):
    df = pd.DataFrame.from_dict(data)
    df.to_csv(file_path, mode='a', header=not os.path.exists(file_path),index=False)

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