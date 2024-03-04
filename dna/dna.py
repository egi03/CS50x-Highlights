import csv
import sys


def main():

    # TODO: Check for command-line usage
    if len(sys.argv) != 3:
        print("Usage: python dna.py data.csv sequence.txt")

    # TODO: Read database file into a variable
    data = []
    with open(sys.argv[1], "r") as file:
        reader = csv.reader(file)
        # Populating 2D array data
        for row in reader:
            L = len(row)
            tmp = []
            for i in range(L):
                tmp.append(row[i])
            data.append(tmp)

    # TODO: Read DNA sequence file into a variable
    with open(sys.argv[2], "r") as file:
        reader = csv.reader(file)
        for row in reader:
            s = row[0]

    # TODO: Find longest match of each STR in DNA sequence
    strs = []
    for i in range(1, L, 1):
        strs.append(longest_match(s, data[0][i]))

    # TODO: Check database for matching profiles
    for i in range(1, len(data), 1):
        z = 1
        for j in range(1, L, 1):
            if (int(data[i][j]) == strs[j - 1]):
                z = z + 1
        if z == L:
            print(data[i][0])
            return
    print("No match")
    return


def longest_match(sequence, subsequence):
    """Returns length of longest run of subsequence in sequence."""

    # Initialize variables
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    # Check each character in sequence for most consecutive runs of subsequence
    for i in range(sequence_length):

        # Initialize count of consecutive runs
        count = 0

        # Check for a subsequence match in a "substring" (a subset of characters) within sequence
        # If a match, move substring to next potential match in sequence
        # Continue moving substring and checking for matches until out of consecutive matches
        while True:

            # Adjust substring start and end
            start = i + count * subsequence_length
            end = start + subsequence_length

            # If there is a match in the substring
            if sequence[start:end] == subsequence:
                count += 1

            # If there is no match in the substring
            else:
                break

        # Update most consecutive matches found
        longest_run = max(longest_run, count)

    # After checking for runs at each character in seqeuence, return longest run found
    return longest_run


main()
