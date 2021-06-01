# Import DictWriter class from CSV module
from csv import DictWriter


def write_dict_to_csv(filename, dict):

    # Open your CSV file in append mode
    # Create a file object for this file
    with open(filename, 'a') as f_object:
        # Pass the file object and a list
        # of column names to DictWriter()
        # You will get a object of DictWriter
        dictwriter_object = DictWriter(f_object, fieldnames=dict.keys())

        # Pass the dictionary as an argument to the Writerow()
        dictwriter_object.writerow(dict)

        # Close the file object
        f_object.close()