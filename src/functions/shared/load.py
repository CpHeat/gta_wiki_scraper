import csv

# Save data in a csv file
def load_data_to_csv(data_list:dict, csv_output:str, fieldnames: tuple):
    with open(csv_output, "w", newline='', encoding='utf-8') as output:
        writer = csv.DictWriter(output, fieldnames = fieldnames, delimiter = ",")
        writer.writeheader()
        for data in data_list:
            writer.writerow(data)
    print(f"CSV file created : {csv_output}")