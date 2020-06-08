TUNING_RANGES = {
    'kp': [0, 10],
    'ki': [0, 10],
    'kd': [0, 10],
}
def optimize_pid(Runner, OptimizerClass):
    opt = OptimizerClass(TUNING_RANGES)
    kp, ki, kd = opt.select()
def calc_penalty(Runner, kp, ki, kd):
    runner = Runner(kp=kp, ki=ki, kd=kd)
    results = runner.run()
    target = runner.target_temp
    measured = np.array(results['temp'])
    gt = measured > target
    gt_penalty = 10
    lt_penalty = 1
    sum_gt_penalty = (gt_penalty * (measured[gt] - target)).sum()
    sum_lt_penalty = (lt_penalty * (target - measured[~gt])).sum()
    return sum_gt_penalty + sum_lt_penalty
