from pathlib import Path
import schedule
import time

def delete_files_by_path():
    for f in Path('./static/uploaded_files_for_recog').glob('*.jpg'):
        try:
            f.unlink()
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))


def func():
    print("Geeksforgeeks")
  
schedule.every(1).minutes.do(func)

schedule.every(5).minutes.do(delete_files_by_path)

# Loop so that the scheduling task
# keeps on running all time.
while True:
  
    # Checks whether a scheduled task 
    # is pending to run or not
    schedule.run_pending()
    time.sleep(1)