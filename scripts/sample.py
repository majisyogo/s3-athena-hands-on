# Tool
import boto3
import time



#1.【Setting】
REGION = "ap-northeast-1"
S3_OUTPUT = "s3://bucket-name/query-results/"
DATABASE = "project_database"
ATHENA_SQL_FILE = "queries/create_table.sql"

QUICKSIGHT_ACCOUNT_ID = "123456789012"  # ←Use your own account number.
QUICKSIGHT_NAMESPACE = "default"
DATASET_NAME = "AnalyticsDataset"
	DATA_SOURCE_NAME = "AthenaDataSource"


# Create Athena client
athena = boto3.client("athena", region_name=REGION)

# Read SQL file
with open(ATHENA_SQL_FILE, "r") as f:
    query_string = f.read()

# Execute Athena query
response = athena.start_query_execution(
    QueryString=query_string,
    QueryExecutionContext={"Database": DATABASE},
    ResultConfiguration={"OutputLocation": S3_OUTPUT}
)
query_id = response["QueryExecutionId"] #Athena assigns query ID.
print(f"Query ID is {query_id}")


# Wait until the query is finished
while True:
    result = athena.get_query_execution(QueryExecutionId=query_id)
    status = result["QueryExecution"]["Status"]["State"]
    if status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
        break
    print("Waiting for Athena query to complete...")
    time.sleep(3)

print(f"Athena query finished with status: {status}")
if status != "SUCCEEDED":
    raise Exception(f"Athena query failed with status: {status}")

# ----------------------
# Create QuickSight client
# ----------------------
qs = boto3.client("quicksight", region_name=REGION)

# Create Athena data source in QuickSight (skip if exists)
try:
    qs.create_data_source(
        AwsAccountId=QUICKSIGHT_ACCOUNT_ID,
        DataSourceId=DATA_SOURCE_NAME,
        Name=DATA_SOURCE_NAME,
        Type="ATHENA",
        DataSourceParameters={
            "AthenaParameters": {"WorkGroup": "primary"}
        },
        Permissions=[],
        SslProperties={"DisableSsl": False}
    )
    print("QuickSight data source created.")
except qs.exceptions.ResourceExistsException:
    print("QuickSight data source already exists, using existing one.")

# Create QuickSight dataset
try:
    qs.create_data_set(
        AwsAccountId=QUICKSIGHT_ACCOUNT_ID,
        DataSetId=DATASET_NAME,
        Name=DATASET_NAME,
        PhysicalTableMap={
            "SalesTable": {
                "RelationalTable": {
                    "DataSourceArn": f"arn:aws:quicksight:{REGION}:{QUICKSIGHT_ACCOUNT_ID}:datasource/{DATA_SOURCE_NAME}",
                    "Catalog": "AwsDataCatalog",
                    "Schema": DATABASE,
                    "Name": "sales",
                    "InputColumns": [
                        {"Name": "date", "Type": "STRING"},
                        {"Name": "product", "Type": "STRING"},
                        {"Name": "quantity", "Type": "INTEGER"},
                        {"Name": "price", "Type": "DECIMAL"}
                    ]
                }
            }
        },
        ImportMode="DIRECT_QUERY"
    )
    print("QuickSight dataset created.")
except qs.exceptions.ResourceExistsException:
    print("QuickSight dataset already exists, skipping creation.")
