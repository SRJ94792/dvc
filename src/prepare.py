import os
import random
import re
import sys
import xml.etree.ElementTree
import yaml

def process_posts(input_lines, fd_out_train, fd_out_test, target_tag, split):
    """
    Process the input lines and write the output to the output files.

    Args:
        input_lines (list): List of input lines.
        fd_out_train (file): Output file for the training data set.
        fd_out_test (file): Output file for the test data set.
        target_tag (str): Target tag.
        split (float): Test data set split ratio.
    """
    num = 1
    for line in input_lines:
        try:
            fd_out = fd_out_train if random.random() > split else fd_out_test
            attr = xml.etree.ElementTree.fromstring(line).attrib

            pid = attr.get("Id", "")
            label = 1 if target_tag in attr.get("Tags", "") else 0
            title = re.sub(r"\s+", " ", attr.get("Title", "")).strip()
            body = re.sub(r"\s+", " ", attr.get("Body", "")).strip()
            text = title + " " + body

            fd_out.write(f"{pid}\t{label}\t{text}\n")

            num += 1
        except Exception as ex:
            sys.stderr.write(f"Skipping the broken line {num}: {ex}\n")

def main():
    # Load parameters from params.yaml
    params = yaml.safe_load(open("params.yaml"))["prepare"]

    # Check for correct number of arguments
    if len(sys.argv) != 2:
        sys.stderr.write("Arguments error. Usage:\n")
        sys.stderr.write("\tpython prepare.py data-file\n")
        sys.exit(1)

    # Parameters for data split
    split = params["split"]
    random.seed(params["seed"])

    input_file = sys.argv[1]
    output_train = os.path.join("data", "prepared", "train.tsv")
    output_test = os.path.join("data", "prepared", "test.tsv")

    # Create output directory if it doesn't exist
    os.makedirs(os.path.join("data", "prepared"), exist_ok=True)

    # Read input file with UTF-8 encoding to avoid decoding errors
    input_lines = []
    with open(input_file, encoding="utf-8") as fd_in:
        input_lines = fd_in.readlines()

    # Open output files with UTF-8 encoding
    fd_out_train = open(output_train, "w", encoding="utf-8")
    fd_out_test = open(output_test, "w", encoding="utf-8")

    # Process and split the posts
    process_posts(
        input_lines=input_lines,
        fd_out_train=fd_out_train,
        fd_out_test=fd_out_test,
        target_tag="<r>",
        split=split,
    )

    # Close output files
    fd_out_train.close()
    fd_out_test.close()

if __name__ == "__main__":
    main()
