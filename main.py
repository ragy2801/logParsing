import subprocess
from re import split
from multiprocessing import Process
import logging

# run with: python basic_multiprocess_pings.py www.google.com www.python.org www.github.com

logFile = "special_Log.log"
logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%m/%d/%Y %H:%M:%S",
                    filename=logFile, encoding='utf-8')


def handle_Trace(time1=0, time2=0, time3=0, ip=""):
    if int(time1) > 30 or int(time2) > 30 or int(time3) > 30:
        logging.info(f"Problem with {ip}: took to long to trace at times: {time1}, {time2}, {time3} ")


def handle_data(name, received=0, sent=0):
    # parse and process data based on threshold
    thresholds = {
        'Bytes': [2000000000, 350000000],
        'Unicast packets': [300000, 2000000],
        'Non-unicast packets': [15000, 90000],
        'Discards': [3, 5],
        'Errors': [2, 5],
        'Unknown protocols': [0, 0]
    }

    if thresholds[name][0] < int(received) or thresholds[name][1] < int(sent):
        logging.info(f"Problem with {name}: Sent or Receiver too large ar (r,s) {received}, {sent}")



def handle_ping(raw):
    # check if there is a packet lost received == sent
    if raw[2] == raw[4]:
        logging.info(f"Problem with Packets: Sent or Receiver too large at (r,s) {raw[4]}, {raw[2]}")


def getPing():
    counter = 1

    if proto_stats.returncode == 0:
        for line in proto_stats.stdout.splitlines():
            if counter == 9:
                raw = split('\W\s', line)
                handle_ping(raw[2:7])
            counter += 1
    else:
        print("Command Failed")


def getNetStats():
    counter = 1
    if net_stats.returncode == 0:
        for line in net_stats.stdout.splitlines():
            if counter < 5:
                counter += 1
                continue
            raw = split('\s\W+', line)

            if not raw[0] == "Errors":
                handle_data(*raw)
    else:
        print("Command Failed")


def getTrace():
    counter = 1

    if trace_stats.returncode == 0:
        for line in trace_stats.stdout.splitlines():
            if counter < 5:
                counter += 1
                continue
            raw = split('\s\D+', line)

            if not raw[0] == "Errors":
                handle_Trace(*raw[2:6])
    else:
        print("Command Failed")


if __name__ == '__main__':
    proto_stats = subprocess.run(["ping", 'www.google.com'], text=True, capture_output=True)
    Process(target=getPing(), args=(proto_stats,), daemon=True).start()

    trace_stats = subprocess.run(["tracert", 'www.google.com'], text=True, capture_output=True)
    Process(target=getTrace(), args=(trace_stats,), daemon=True).start()

    net_stats = proto_stats = subprocess.run(["netstat", '-e'], text=True, capture_output=True)
    Process(target=getNetStats(), args=(net_stats,), daemon=True).start()
