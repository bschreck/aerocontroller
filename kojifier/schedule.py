from pathlib import Path
from crontab import CronTab
import fire


def schedule(temp=25, humidity=90, slack=1, output_log='~/.kojifier/log.txt'):
    output_log = Path(output_log).expanduser()
    output_log.parent.mkdir(parents=True, exist_ok=True)
    with CronTab(user=True) as cron:
        iter = cron.find_command('kojify_adjust')
        for job in iter:
            cron.remove(job)
        job = cron.new(command=f'kojify_adjust --temp={temp} --humidity={humidity} --slack={slack} > {output_log}')
        job.minute.every(1)
    print('cron.write() was just executed')


if __name__ == '__main__':
    fire.Fire(schedule)
