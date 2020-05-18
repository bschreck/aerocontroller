from pathlib import Path
from crontab import CronTab
import fire


def schedule(output_log='~/.kojifier/log.txt'):
    Path(output_log).expanduser().mkdir(parents=True, exist_ok=True)
    with CronTab(user=True) as cron:
        job = cron.new(command=f'kojify_adjust > {output_log}')
        job.minute.every(1)
    print('cron.write() was just executed')


if __name__ == '__main__':
    fire.Fire(schedule)
