from pathlib import Path
from crontab import CronTab
from subprocess import check_output
import fire


def schedule(temp=25, humidity=85, slack=1, output_log='~/.kojifier/log.txt'):
    print(f"Scheduling kojifier with temp={temp}, humidity={humidity}, slack={slack}, log={output_log}")
    output_log = Path(output_log).expanduser()
    output_log.parent.mkdir(parents=True, exist_ok=True)
    cmd = check_output(['which', 'kojify_adjust'])
    cmd = cmd.decode('utf-8').strip()
    with CronTab(user=True) as cron:
        iter = cron.find_command('kojify_adjust')
        for job in iter:
            cron.remove(job)
        job = cron.new(command=f'{cmd} --temp={temp} --humidity={humidity} --slack={slack} >> {output_log} 2>&1')

        job.minute.every(1)
    print('cron.write() was just executed')


def cli():
    fire.Fire(schedule)
