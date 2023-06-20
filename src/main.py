from mail import fetch_mails,write_message_ids,update_labels
from inference import infer_mail
from utils import append_job_data
import json
from config import JOB_LABEL_ID
import argparse
from logger import logger

BATCH = 10

def main(args):
    mails,message_ids = fetch_mails(nResults=args.mails)
    
    processed_message_ids = []
    job_application_msg_ids = []
    data = []
    for i_batch in range(0,len(mails),BATCH):
        data = []
        processed_message_ids = []
        job_application_msg_ids = []
        for i,mail_payload in enumerate(mails[i_batch:i_batch+BATCH]):
            try:
                inferred_json_data = infer_mail(mail_payload,type=args.inference_type)
                inferred_data = json.loads(inferred_json_data)
                
                if inferred_data.get("is_job_application"):
                    data.append(inferred_data)
                    job_application_msg_ids.append(message_ids[i])

                processed_message_ids.append(message_ids[i])

            except Exception as e:
                logger.error('Error: MessageId: %s , Mail Subject %s',mail_payload["message_id"],mail_payload["title"], exc_info=e)
        
        write_message_ids(processed_message_ids)
        append_job_data(data, args.output)
        update_labels(JOB_LABEL_ID,job_application_msg_ids)
                    
    return



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mails", type=int,default=100)
    parser.add_argument("-o", "--output", type=str, default='job_application_status.csv')
    parser.add_argument("-i", "--inference_type", type=str, default="openai-gpt")
    args = parser.parse_args()
    main(args)