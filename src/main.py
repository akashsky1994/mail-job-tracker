from mail import fetch_mails
from inference import infer_mail
from utils import append_job_data

def main():
    mails,nextpageToken = fetch_mails()

    data = []
    for content in mails:
        data.append(infer_mail(content))

    append_job_data(data)
    return



if __name__ == '__main__':
    main()