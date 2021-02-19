import os
import configparser
from azure.storage.blob import BlobServiceClient

# read config
config = configparser.ConfigParser()
config.read('azure.conf')

def download_data(participant, download_path):
    participant = str(participant)

    #download_path = r"D:\HABitsLab\WristDataChecks\{}".format(participant)
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    try:
        # Create the BlobServiceClient that is used to call the Blob service for the storage account
        conn_str = config['azure']['connectionstring']
        blob_service_client = BlobServiceClient.from_connection_string(conn_str=conn_str)

        # specify the name of the container. (For SenswWhy this is the participant ID
        container_name = participant

        # List the blobs in the container
        print("\nDownloading blobs in the container")
        container = blob_service_client.get_container_client(container=container_name)
        generator = container.list_blobs()
        count = 0

        for blob in generator:
            count += 1

            # print("\t Blob name: " + blob.name)

            # create the blob client
            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob=blob.name)

            # download path
            full_path_to_file = os.path.join(download_path, blob.name)
            # print("\nDownloading blob to " + full_path_to_file)

            if (not os.path.exists(full_path_to_file)):
                # download the blob to local
                with open(full_path_to_file, "wb") as my_blob:
                    my_blob.writelines([blob_client.download_blob().readall()])

            print(f'\rDownloaded|{count}| blobs', end='\r')

    except Exception as e:
        print(e)
    print()


# Main method.
if __name__ == '__main__':
    download_data(502)