import datetime
import json
from multiprocessing import Queue
from threading import Thread
from base import driver_code
from market_data import get_main_market_data


def base_structue():
    return {"time": "", "match_name": "", "market_data": []}


def export_match_data(match_name, match_data):
    base_dict = base_structue()
    base_dict["time"] = str(datetime.datetime.now())
    base_dict["match_name"] = match_name
    base_dict["market_data"] = match_data

    with open("game_data.json", "r") as f:
        # Read the JSON data into a dictionary.
        data = json.load(f)
    data.append(base_dict)
    with open("game_data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def run_driver(driver_num, queue):
    try:
        driver = driver_code(driver_num)  # You can use any Selenium WebDriver here
        # Add your automation code for the driver here

        result = {"result_value": []}
        if driver_num == 0:
            result["result_value"] = get_main_market_data(driver, True)
        else:
            result["result_value"] = get_main_market_data(driver, False)
        driver.quit()

        queue.put(result)  # Put the result in the queue
    except Exception as e:
        raise e


if __name__ == "__main__":
    num_drivers = 2  # Number of drivers you want to run

    threads = []
    result_queue = Queue()  # Create a queue to store the results

    for i in range(num_drivers):
        t = Thread(target=run_driver, args=(i, result_queue))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()

    # Retrieve the results from the queue
    results = []
    match_name = ""
    match_data = []
    while not result_queue.empty():
        result = result_queue.get()
        match_name = result.get("result_value")[0]
        match_data.append(result.get("result_value")[1])
        results.append(result)

    export_match_data(match_name, match_data)
