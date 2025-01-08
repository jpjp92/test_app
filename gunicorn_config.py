# gunicorn_config.py
workers = 4
threads = 4
timeout = 3000
max_requests = 1000
max_requests_jitter = 50
worker_class = 'gthread'
worker_tmp_dir = '/dev/shm'

# Memory limits
worker_max_memory_per_child = 4800000  # 4800MB
