from crontab import CronTab


def setup_cron():
    cron = CronTab(user=True)
    job = cron.new(command='python $HOME/dev/mail-job-tracker/src/main.py --mails 1000 --output $HOME/Documents/SyncedDocuments/job_application_status.csv') 
    job.hour.every(12)
    cron.write()


if __name__ == "__main__":
    setup_cron()