# API Gateway variables (edit as needed)
# Use the APIGW_ prefix so the main script can tell these came from a file and only
# apply them when CLI parameters are not supplied (CLI overrides file values).

# Example values - replace with your real API ID / region / lambda ARN
$APIGW_ApiId = "nqseqiylz5"
$APIGW_Region = "us-east-1"
$APIGW_LambdaFunctionName = "RiftRewindOrchestrator"
$APIGW_LambdaArn = "arn:aws:lambda:us-east-1:588752324088:function:RiftRewindOrchestrator"

# Set this to $true to run the fix script without interactive confirmation
$APIGW_AutoApprove = $false

# SECURITY NOTE:
# - Do NOT commit secrets or sensitive ARNs to public repos.
# - This file is convenient for local use; consider adding it to .gitignore.
