import re

# Sample input with multiple tables
text = """"""
# Regular expression to match tables separated by empty lines
regex = r'((?:[^\n]*\|[^\n]*\|[^\n]*\n?)+)'

# Find all tables
tables = re.findall(regex, text.strip())

pure_text = re.sub(regex, '', text)

# Function to remove extra lines before and after each match
def extract_surrounding_text(text, regex):
    matches = re.finditer(regex, text)
    results = []

    for match in matches:
        start = match.start()
        end = match.end()

        # Extract 2 lines above and below the match
        # Get text before the match
        before_match = text[:start].strip().split('\n')[-3:]
        # print(before_match)

        # if re.finditer(regex,  before_match):
        #         before_match = []  # Exclude if it's an empty table pattern

        # Get text after the match
        after_match = text[end:].strip().split('\n')[:3]

        # if re.finditer(regex, after_match):
        #         after_match = []  # Exclude if it's an empty table pattern

        # Extract the matched table content
        table_content = match.group(0).strip()

        # Append the context along with the table content
        results.append(('\n'.join(before_match), table_content, '\n'.join(after_match)))

    return results

# Extract surrounding text along with matched tables
results = extract_surrounding_text(text, regex)

# Print the surrounding content and matched tables
for before, table, after in results:
    #print("Before Match:")
    #print(before)
    before_matches = re.finditer(regex, before)
    before_total_length = sum(len(match.group(0)) for match in before_matches)

    if before_total_length == 0:
       print(before)



    print(table)


    after_matches = re.finditer(regex, after)
    after_total_length = sum(len(match.group(0)) for match in after_matches)


    if after_total_length == 0:
       print(after)

    print("###################Next Chunck###############")


