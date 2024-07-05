import boto3
from botocore.exceptions import NoCredentialsError
import time
from datetime import datetime
import os
from lib_credentials import starting_credencials as credentials
import json
from lib_applogs import log_message as log

log('info', 'Starting application')

log('info', f'Reading settings.json file')
with open ('settings.json', "r") as appConfig:
    config = json.load(appConfig)
    timeout_to_add_bucket = config['app_parameters']['time_insert_bucket']
    polling_interval = int(config['app_parameters']['polling_interval'])

log('info', f'To insert other bucket: {timeout_to_add_bucket} seconds')
log('info', f'Polling interval as: {polling_interval} seconds')

log('info', f'Getting all credentials')

credential_list = credentials(timeout_to_add_bucket)

def execute_all():
    for bucket, access_k, secret_k in credential_list:
        BUCKET_NAME = bucket
        AWS_ACCESS_KEY = access_k
        AWS_SECRET_KEY = secret_k
        log('info', f'Starting to send to {BUCKET_NAME}')
        def upload_to_aws(local_file, bucket, s3_file):
            s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
            try:
                s3.upload_file(local_file, bucket, s3_file)
                print(f'Successfully uploaded {s3_file} to {bucket}')
                log('info',f'Successfully uploaded {s3_file} to {bucket}')
                return True
            except FileNotFoundError:
                print("The file was not found")
                log('info',"The file was not found")
                return False
            except NoCredentialsError:
                print("Credentials not available")
                log('info',"Credentials not available")
                return False

        def get_directories():
            with open ('directories_set.json', "r") as pathConfig:
                config = json.load(pathConfig)
                directories_config = config[bucket]
            return directories_config

        def copy_files(consuption_file, destination_backup):
            
            if os.path.isfile(consuption_file):
                with open(consuption_file, 'rb') as src_file:
                    data = src_file.read()
                    dest_file_path = os.path.join(destination_backup, os.path.basename(consuption_file))
                    print(dest_file_path)
                    with open(dest_file_path, 'wb') as dest_file:
                        dest_file.write(data)

        def list_files():
            while True:
                directories_all = get_directories()
                directories_list = directories_all.get('directories')
                backup_path = directories_all.get('backup_path')

                for directory in directories_list:
                    try:
                        file_list = []
                        for file_name in os.listdir(directory):
                            if os.path.isfile(os.path.join(directory, file_name)):
                                file_list.append(file_name)
                            else:
                                print(f"No files found in {directory}")
                                log('warning', f"No files found in {directory}")
                        
                        dir_backup_list = backup_path
                        counting = len(file_list)
                        print(f'{counting} files found in {directory}')
                        log('info', f'{counting} files found in {directory}')
                        for file in file_list:
                            print(file)
                            consuption_file = os.path.join(directory, file)
                            s3_file = file
                            upload_to_aws(consuption_file, BUCKET_NAME, s3_file)
                            for path_bkp in dir_backup_list:
                                copy_files(consuption_file, path_bkp)
                            print(consuption_file)
                            print(s3_file)
                            print(path_bkp)
                            print(f"The file {file} was sent to AWS S3 and copied in the BACKUP folder.")
                            log('info', f"The file {file} was sent to AWS S3 and copied in the BACKUP folder.")
                            time.sleep(5)
                            os.remove(consuption_file)
                    except Exception as e:
                        log('error', f"There is an error during list file attempt: {e}")
                
                return file_list
        list_files()
if __name__ == "__main__":
    while True:
        execute_all()
        print(f"Sleeping for {polling_interval} seconds before next run...")
        log('info', f"Sleeping for {polling_interval} seconds before next run...")
        time.sleep(polling_interval)