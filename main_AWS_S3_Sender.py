import boto3
from botocore.exceptions import NoCredentialsError
import time
from datetime import datetime
import datetime
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
    copy_registries = config['app_parameters']['copy_registries']

log('info', f'To insert other bucket: {timeout_to_add_bucket} seconds')
log('info', f'Polling interval as: {polling_interval} seconds')

log('info', f'Getting all credentials')

credential_list = credentials(timeout_to_add_bucket)

def countdown(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        print(time_format, end='\r')
        time.sleep(1)
        seconds -= 1
    print('00:00')

def reg_copies(data, filename=copy_registries):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(filename, 'a') as f:
        f.write(f'{timestamp}: {data}\n')

def check_dir_modifications():
    for bucket, access_k, secret_k in credential_list:
        def get_dirs():
            with open ('directories_set.json', "r") as pathConfig:
                config = json.load(pathConfig)
                directories_config = config[bucket]
                
            return directories_config
        def listing_first_files():
            directories_all = get_dirs()
            directories_list = directories_all.get('directories')
            sub_dir_conf = directories_all.get('subdirectory')

            for directory in directories_list:

                if sub_dir_conf == 'True':
                        def get_all_file_paths(directory):
                            flist = []
                            try:
                                for root, _, files in os.walk(directory):
                                    for file in files:
                                        flist.append(os.path.join(root, file))
                                return flist
                            except:
                                pass
                        get_all_file_paths(directory)
                else:

                    flist = []
                    try:
                        for file_name in os.listdir(directory):
                            if os.path.isfile(os.path.join(directory, file_name)):
                                flist.append(file_name)
                    except:
                        pass



    firstime = listing_first_files()
    time.sleep(10)
    secondtime = listing_first_files()
    
    if firstime == secondtime and firstime is not []:
        return True
    else:
        return False





def execute_all():
    for bucket, access_k, secret_k in credential_list:
        print(f'\nChecking files for: {bucket}')
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
                reg_copies(f'FROM;{local_file};TO;S3;{bucket}')
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

        def copy_files(consuption_file, destination_backup, backup_conf):
                            
            if backup_conf == 'True':
                print('Backup in progress...')
                try:  
                    if os.path.isfile(consuption_file):
                        with open(consuption_file, 'rb') as src_file:
                            data = src_file.read()
                            dest_file_path = os.path.join(destination_backup, os.path.basename(consuption_file))
                            print(f'Copy in: {dest_file_path}')
                            with open(dest_file_path, 'wb') as dest_file:
                                dest_file.write(data)
                            reg_copies(f'FROM;{consuption_file};TO;BKP;{dest_file_path}')
                except Exception as e:
                        log('error', f"There is an error during BACKUP attempt: {e}")
                        pass
            else:
                print('Process without backup configured.')
                log('info', f'backup_conf from directory_set.json is not "True"')

        


        def list_files():
            directories_all = get_directories()
            directories_list = directories_all.get('directories')
            backup_path = directories_all.get('backup_path')
            backup_conf = directories_all.get('backup_conf')
            sub_dir_conf = directories_all.get('subdirectory')

            for directory in directories_list:

                if sub_dir_conf == 'True':
                        def get_all_file_paths(directory):
                            file_list = []
                            for root, _, files in os.walk(directory):
                                for file in files:
                                    file_list.append(os.path.join(root, file))
                            return file_list
                        file_list = get_all_file_paths(directory)
                        

                else:

                    file_list = []
                    try:
                        for file_name in os.listdir(directory):
                            if os.path.isfile(os.path.join(directory, file_name)):
                                file_list.append(file_name)
                            else:
                                print(f"No files found in {directory}")
                                log('warning', f"No files found in {directory}")
                    except Exception as e:
                        print(f'Error while trying list files in {directory}')
                        log('error', f'Error while trying list files in {directory}')
                        pass
                    
                dir_backup_list = backup_path
                if file_list == []:
                    print(f"No files found in {directory}")
                    log('warning', f"No files found in {directory}")
                else:
                    counting = len(file_list)
                    print(f'=== {counting} objects found in {directory}')
                    log('info', f'{counting} objects found in {directory}')
                for file in file_list:
                    
                    consuption_file = os.path.join(directory, file)
                    print(f'\nWorking on file: {consuption_file}')
                    s3_file = file

                    upload_to_aws(consuption_file, BUCKET_NAME, s3_file)
                    for path_bkp in dir_backup_list:
                        copy_files(consuption_file, path_bkp, backup_conf)
                    print(f'The file "{file}" was sent to AWS S3 and copied in the BACKUP folder.')
                    log('info', f'The file "{file}" was sent to AWS S3 and copied in the BACKUP folder.')
                    time.sleep(5)
                    os.remove(consuption_file)
            
        list_files()
if __name__ == "__main__":
    while True:
        result_test = check_dir_modifications()
        while not result_test:
            result_test = check_dir_modifications()
        execute_all()
        print(f"Sleeping for {polling_interval} seconds before next run...\n")
        # countdown(polling_interval)
        time.sleep(polling_interval)
        log('info', f"Sleeping for {polling_interval} seconds before next run...")