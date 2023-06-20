from crontab import CronTab


def setup_cron():
    cron = CronTab(user=True)
    job = cron.new(command='cd $HOME/dev/mail-job-tracker && poetry run python src/main.py --mails 100 --output $HOME/Documents/SyncedDocuments/job_application_status.csv') 
    job.hour.every(1)
    cron.write()


if __name__ == "__main__":
    setup_cron()