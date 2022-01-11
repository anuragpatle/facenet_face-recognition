from pathlib import Path
import schedule
import time

def delete_files_by_path():
    for f in Path('./static/uploaded_files_for_recog').glob('*.jpg'):
        try:
            f.unlink()
            print("Cleaned the directory -> ./static/uploaded_files_for_recog")
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))


def cleanup_running_tick():
    print("Cleanup is running ..")
  
schedule.every(2).seconds.do(cleanup_running_tick)

schedule.every(5).minutes.do(delete_files_by_path)

# Loop so that the scheduling task
# keeps on running all time.
while True:
  
    # Checks whether a scheduled task 
    # is pending to run or not
    schedule.run_pending()
    time.sleep(1)