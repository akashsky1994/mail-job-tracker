from mail import fetch_mails,write_message_ids,update_labels
from inference import infer_mail
from utils import append_job_data
import json
from config import JOB_LABEL_ID
import argparse

def main(nResults):
    mails,message_ids = fetch_mails(nResults=nResults)
    
    processed_message_ids = []
    job_application_msg_ids = []
    data = []
    for i,mail_payload in enumerate(mails):
        try:
            inferred_json_data = infer_mail(mail_payload,type="openai-gpt")
            print(inferred_json_data)
            inferred_data = json.loads(inferred_json_data)
            
            if inferred_data.get("is_job_application"):
                data.append(inferred_data)
                job_application_msg_ids.append(message_ids[i])
            processed_message_ids.append(message_ids[i])
        except Exception as e:
            print(e)
            print(inferred_json_data)
            
    print(data)
    if len(data)>0:
        append_job_data(data)
    
    write_message_ids(processed_message_ids)
    
    update_labels(JOB_LABEL_ID,job_application_msg_ids)
    return



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mails", type=int,default=100)
    args = parser.parse_args()
    main(args.mails)