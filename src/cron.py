from crontab import CronTab


def setup_cron():
    cron = CronTab(user=True)
    job = cron.new(command='source $HOME/dev/mail-job-tracker/run.sh') 
    job.hour.every(1)
    cron.write()


if __name__ == "__main__":
    setup_cron()