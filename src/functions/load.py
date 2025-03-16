import csv

def load_data_to_csv(data_list: dict, csv_output: str, fieldnames: tuple) -> None:
    """
    Saves the data in a csv file

    :param data_list: data to save
    :param csv_output: output csv file name
    :param fieldnames: csv fieldnames
    """
    with open(csv_output, "w", newline='', encoding='utf-8') as output:
        writer = csv.DictWriter(output, fieldnames = fieldnames, delimiter = ",")
        writer.writeheader()
        for data in data_list:
            writer.writerow(data)
    print(f"CSV file created : {csv_output}")