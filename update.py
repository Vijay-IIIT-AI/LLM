def filter_top_results(df, threshold=0.6):
    """
    Filters the final dataframe to remove rows where the rerank_score is below the given threshold.

    :param df: DataFrame containing 'rerank_score' column.
    :param threshold: Score threshold for filtering (default: 0.6).
    :return: Filtered DataFrame.
    """
    return df[df['rerank_score'] >= threshold]
