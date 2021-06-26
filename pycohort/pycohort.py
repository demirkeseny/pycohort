# # packages needed




def calculate_mean(some_list):
    """
    Function to calculate the mean of a dataset.
    Takes the list as an input and outputs the mean.
    """

    return (1.0 * sum(some_list) / len(some_list))

def calculate_stdev(some_list, sample=True):
    """
    Function to calculate the standard deviation of a dataset.
    Takes the list as an input and outputs the standard deviation.
    """
    
    import math

    if sample:
        n = len(some_list) - 1
    else:
        n = len(some_list)

    mean = calculate_mean(some_list)

    sigma = 0

    for d in some_list:
        sigma += (d - mean) ** 2

    sigma = math.sqrt(sigma / n)

    return sigma

def calculate_median(some_list):
    """
    Function to calculate the median of a dataset.
    Takes the list as an input and outputs the median.
    """

    ordered = some_list.sort_values(ascending=True).reset_index(drop=True)

    return ordered[(int(len(ordered)/2))]

def cohort_preprocess(df):
    """
    Function to prepare dataset for the cohort visualization.
    Takes the a dataframe and converts it to a NxN matrix dataframe.
    """
    
    import numpy as np
    import pandas as pd
    from datetime import timedelta, date, datetime
    
    df['metric_month'] = pd.to_datetime(df.metric_month)
    df['creation_date'] = pd.to_datetime(df.creation_date)
    df['last_active_month'] = pd.to_datetime(df.last_active_month)
    df.set_index('id', inplace=True)
    df['CohortGroup'] = df.groupby(level=0)['metric_month'].min().apply(lambda x: x.strftime('%Y-%m'))
    df.reset_index(inplace=True)
    cohorts = df.groupby(['CohortGroup', 'metric_month']).agg({'id':pd.Series.nunique})
    cohorts.rename(columns={'id': 'TotalAccounts'}, inplace=True)
    
    def cohort_period(df):
        df['CohortPeriod'] = np.arange(len(df)) + 1
        return df

    cohorts = cohorts.groupby(level=0).apply(cohort_period)
    cohorts.reset_index(inplace=True)
    cohorts.set_index(['CohortGroup', 'CohortPeriod'], inplace=True)
    cohort_group_size = cohorts['TotalAccounts'].groupby(level=0).first()
    user_retention = cohorts['TotalAccounts'].unstack(0).divide(cohort_group_size, axis=1)
    user_retention = user_retention.iloc[1:,:len(user_retention)-1]
    return user_retention

def cohort_viz(df):
    """
    Function to visualize the cohort analysis.
    Takes matrix dataframe as an input and outputs the sns heatmap chart with cohort retention rates.
    """
    import seaborn as sns
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    from IPython.display import display
    
    plt.style.use('fivethirtyeight')
    width, height = plt.figaspect(4)
    fig = plt.figure(figsize=(width,height), dpi=400)
    plt.style.use('fivethirtyeight')
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = 'DejaVu Sans'
    plt.rcParams['font.monospace'] = 'Ubuntu Mono'
    plt.rcParams['font.size'] = 4
    plt.rcParams['axes.labelsize'] = 6
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 6
    plt.rcParams['xtick.labelsize'] = 6
    plt.rcParams['ytick.labelsize'] = 6
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.titlesize'] = 12;

    width, height = plt.figaspect(.6)
    fig = plt.figure(dpi=250)

    plt.title("Monthly Retention Rate", fontsize=12, fontweight='bold')
    sns.heatmap(df.T, mask=df.T.isnull(), annot=True, fmt='.2f', cmap='OrRd_r', xticklabels=list(range(1,len(df))))
    plt.xlabel('Periods in Months')
    plt.ylabel('Cohort Groups (Signup Month)')

