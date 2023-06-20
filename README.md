# Job Tracker for Gmail
Simple Python service to manage all your job application mails, track, label and store them into a csv file. We use OpenAI GPT and Falcon-7B to infer the intent and information from the emails.

### How to Setup 
Take a look at the [pyproject.toml](https://github.com/akashsky1994/mail-job-tracker/blob/main/pyproject.toml) for all package requirements. 

We use poetry for package management. Run Poetry install to setup the enviroment from the .toml file.
```
poetry install
```

OPENAI : Add ```OPENAI_API_KEY``` enviroment on your system to use OPENAI apis. 
Falcon-7B : This smaller version of falcon-40b also requires around 20GB memory.

### How to run
```
poetry run python src/main.py --mails 10 --output $HOME/Documents/SyncedDocuments/job_application_status.csv
```
mails argument implies how many mails do you want to infer and analyse

### Setup Cron
```
poetry run python cron.py
```
You can change the periodicity of the cron depending upon your preference. Currently it runs once every 12 hours.

