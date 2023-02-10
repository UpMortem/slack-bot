import time

def retry(func, retries=3, delay=1, exceptions=(Exception,)):
    while retries > 0:
        try:
            return func()
            break
        except exceptions as e:
            retries -= 1
            if retries == 0:
                raise e
            print(f"Failed, retrying... ({retries} attempts remaining)")
            time.sleep(delay)
