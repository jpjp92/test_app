# gunicorn_config.py
workers = 2
threads = 4
timeout = 2000
max_requests = 1000
max_requests_jitter = 50
worker_class = 'gthread'
worker_tmp_dir = '/dev/shm'

# Memory limits
worker_max_memory_per_child = 2200000  # 2200MB
