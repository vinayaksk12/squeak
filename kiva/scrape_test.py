import requests
import shutil

def download_snapshot(url):
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

    return local_filename


download_snapshot("http://s3.kiva.org/snapshots/kiva_ds_csv.zip")
