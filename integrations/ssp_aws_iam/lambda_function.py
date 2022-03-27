import boto3

# you can assign role in the function like below
# ROLE_ARN = 'arn:aws:iam::01234567890:role/my_role'
#
# or you can pass role as an evironment varibale
# ROLE_ARN = os.environ['role_arn']
def aws_session(role_arn=None, session_name=None, external_id=None):
    """
    If role_arn is given assumes a role and returns boto3 session
    otherwise return a regular session with the current IAM user/role
    """
    if role_arn:
        client = boto3.client('sts')
        response = client.assume_role(RoleArn=role_arn, RoleSessionName=session_name, ExternalId=external_id)
        session = boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken'])
        return session
    else:
        return boto3.Session()

def lambda_handler(event, context):
    customer_session = aws_session(role_arn=event['customer_arn'], session_name='SSP-Session', external_id=event['external_id'])
    iam_client = customer_session.client('iam')

    user_list = iam_client.list_users()
    ssp_user_list = {}
    for user in user_list['Users']:
        access_keys = iam_client.list_access_keys(UserName=user.UserName)
        