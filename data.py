Why BLEU or Cosine Similarity Are Not Good for DataFrame Analytics
[1] They measure text similarity, not correctness.
These metrics check if the output text looks like the reference, not if it’s actually right.
[2] They don’t handle numbers or logic well.
They can’t verify if a calculation, filter, or table lookup is correct.
[3] They are sensitive to small wording changes.
Even if two answers mean the same thing, minor differences in wording can lower the score.
[4] They can give high scores to wrong answers.
If a wrong answer sounds similar to the right one, it might still get a high score.

Why Valid/Invalid Evaluation Is Better
[1] It checks if the output is truly correct.
It directly compares the agent’s answer to the expected result.
[2] It works well with numbers, logic, and table data.
It can validate sums, counts, filters, or any computed result from the dataframe.
[3] It doesn’t care about how the answer is written.
As long as the result is correct, different phrasing is acceptable.
[4] It gives clear and simple results.
Each answer is either valid (correct) or invalid (incorrect), which makes evaluation easy.
