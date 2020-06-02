def get_logger(name):
    logger = logging.getLogger(name)
    console = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - auto_fermenter - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.setLevel(logging.INFO)
