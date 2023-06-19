from mail import fetch_mails,write_message_ids
from inference import infer_mail
from utils import append_job_data
import json

def main():
    mails,message_ids = fetch_mails()

    data = []
    for mail_payload in mails:
        inferred_json_data = infer_mail(mail_payload,type="openai-gpt")
        print(inferred_json_data)
        inferred_data = json.loads(inferred_json_data)
        
        if inferred_data.get("is_job_application"):
            data.append(inferred_data)
    print(data)
    if len(data)>0:
        append_job_data(data)
    
    write_message_ids(message_ids)
        
    return



if __name__ == '__main__':
    main()