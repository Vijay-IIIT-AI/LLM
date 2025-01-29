You are given the following markdown table. Please calculate how many batches of 10 rows each are required to process the entire table. Return the number of batches.

Input data:
[Insert the raw markdown table here]

Output:
[Number of batches]


You are given a full table of raw markdown data. Please return the first batch of 10 rows flattened. After that, indicate where to continue from the previous batch. For example, you can return the row number or another identifier to specify the next batch start point. If this is the last batch, return 'None'. Ensure to flatten the data appropriately.

Input data:
[Insert the raw markdown table here]

Output:
{
  "flattened_data": [
    "{row1_description}",
    "{row2_description}",
    "{row3_description}",
    "{row4_description}",
    "{row5_description}",
    "{row6_description}",
    "{row7_description}",
    "{row8_description}",
    "{row9_description}",
    "{row10_description}"
  ],
  "next_batch_start": 11
}
