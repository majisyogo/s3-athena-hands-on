##【Project Overview】
Analyze and visualize sales data using S3 → Athena → QuickSight with AWS CLI.

##【Architecture】
CSV data is stored in data/ folder and uploaded to S3.
Athena tables are created via SQL scripts in queries/.
Athena queries are executed using scripts/run_athena_query.sh.
QuickSight datasets are created via scripts/create_quicksight_dataset.sh.
QuickSight dashboards visualize sales trends, rankings.

##【What I Learned】
Athena requires proper table definitions to query CSV data successfully.
S3 bucket structure affects query paths, so organization is important.
QuickSight datasets can be automated via AWS CLI, saving manual steps.
