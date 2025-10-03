from google.cloud import bigquery

client = bigquery.Client()

# tables
rphst_table = (
    "`ons-fintrans-data-prod.fintrans_visa.retail_performance_high_streets_towns`"
)
sml_table = "`ons-fintrans-data-prod.fintrans_visa.spend_merchant_location`"
spoc_table = "`ons-fintrans-data-prod.fintrans_visa.spend_origin_and_channel`"
nspl_table = "ons-fintrans-data-prod.fintrans_reference.NSPL21_FEB_2024_UK"


def table_dictionary():
    table_name = ["rphst", "sml", "spoc"]
    table_sql = [rphst_table, sml_table, spoc_table]
    tables_dict = dict(zip(table_name, table_sql))
    return tables_dict


def align_df(table, mcg):

    """Create a SQL query for a given table and mcg.
        Read in data for align datasources

    Args:
        table (str): The table to read the data from
            e.g. rphst, sml, spoc
        mcg (str): Choose specific mcg or '' for all MCGs

    Returns:
        pd.DataFrame
    """

    table_values = table_dictionary().keys()
    if table not in table_values:
        raise ValueError(f"Argument table must be one of {table_values}")

    if mcg == "":
        mcg = "%"
    else:
        mcg = mcg

    if table == "rphst":
        where_statement = f"""
        cardholder_location_level = 'All'
        AND mcg like '{mcg}'
        AND merchant_location_level = 'POSTAL_SECTOR'"""
        table = table_dictionary().get("rphst")

    elif table == "sml":
        where_statement = f"""
        cardholder_issuing_level = 'Domestic'
        AND mcg like '{mcg}'  AND
        merchant_location_level = 'POSTAL_AREA'
        AND mcc = 'All'"""
        table = table_dictionary().get("sml")

    elif table == "spoc":
        where_statement = f"""
        cardholder_origin = 'UNITED KINGDOM'
        AND  cardholder_origin_country = 'All'
        AND destination_country = 'UNITED KINGDOM'
        AND mcg like '{mcg}'
        AND mcc = 'All'
        AND merchant_channel = 'Face to Face'"""
        table = table_dictionary().get("spoc")

    sql_aligned = f"""SELECT *
    FROM {table}
    WHERE {where_statement}
    ORDER BY time_period, time_period_value, mcg"""

    df_aligned = client.query(sql_aligned).to_dataframe()

    return df_aligned


def load_rphst(cardholder_level, merchant_level, month_quarter):
    """
    Description:
    - Create a SQL query for a given table

    Args:
    - table: string value specifying table to load

    Returns:
    - pd.DataFrame
    """

    select_statement = "time_period,\
    time_period_value,\
    SUM(spend) AS spend,\
    SUM(transactions) AS transactions,\
    mcg,\
    cardholder_location,\
    merchant_location"

    where_statement = f"""time_period = '{month_quarter}'\
    AND cardholder_location_level = '{cardholder_level}'\
    AND merchant_location_level =  '{merchant_level}'"""

    group_statement = (
        "time_period, time_period_value, mcg, cardholder_location, merchant_location"
    )
    table = table_dictionary().get("rphst")

    sql_highlevel = f"""SELECT {select_statement}
    FROM {table}
    WHERE {where_statement}
    GROUP BY {group_statement}
    ORDER BY {group_statement}"""

    df = client.query(sql_highlevel).to_dataframe()

    return df


def load_spoc(cardholder_level, month_quarter, merchant_channel):
    """
    Description:
    - Create a SQL query for a given table

    Args:
    - table: string value specifying table to load

    Returns:
    - pd.DataFrame
    """

    select_statement = "*"

    where_statement = f"""
    cardholder_origin = 'UNITED KINGDOM'\
    AND  cardholder_origin_country = '{cardholder_level}'\
    AND destination_country = 'UNITED KINGDOM'\
    AND time_period = '{month_quarter}'\
    AND mcc = 'All'\
    AND merchant_channel = '{merchant_channel}'"""

    table = table_dictionary().get("spoc")

    sql_highlevel = f"""SELECT {select_statement}
    FROM {table}
    WHERE {where_statement}"""

    df = client.query(sql_highlevel).to_dataframe()

    return df


def load_nspl():
    """
    Description:
    - Create a SQL query for a given table

    Args:
    - table: string value specifying table to load

    Returns:
    - pd.DataFrame
    """

    select_statement = "*"

    sql_nspl = f"""SELECT {select_statement}
    FROM {nspl_table}"""

    df = client.query(sql_nspl).to_dataframe()

    return df


def load_sml(mcg, merchant_level):

    """Create a SQL query for a given table and mcg.
        Read in data for align datasources

    Args:
        table (str): The table to read the data from
            e.g. rphst, sml, spoc
        mcg (str): Choose specific mcg or '' for all MCGs

    Returns:
        pd.DataFrame
    """

    where_statement = f"""
    cardholder_issuing_level = 'Domestic'
    AND mcg like '{mcg}'
    AND time_period = 'Month'
    AND merchant_location_level = '{merchant_level}'
    AND mcc = 'All'"""
    table = table_dictionary().get("sml")

    sql_sml = f"""SELECT *
    FROM {table}
    WHERE {where_statement}
    ORDER BY time_period, time_period_value, mcg, merchant_location_level"""

    df_sml = client.query(sql_sml).to_dataframe()

    return df_sml
