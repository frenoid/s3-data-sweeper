# S3 Data Sweeper
A simple Python script to watch a directory and then upload files created in that directory to S3

Useful for bulk file transfer situations

## How to run
Clone the repo
```bash
git clone https://github.com/frenoid/s3-data-sweeper.git
```


Install required packages
```bash
pip3 install -r requirements.txt
```

Set up your environment variables
```bash
export AWS_ACCESS_KEY_ID='your-access-key-id'
export AWS_SECRET_ACCESS_KEY='your-secret-access-key'
export S3_ENDPOINT='your-s3-endpoint' # Useful for privately hosted Minio buckets
export S3_BUCKET='your-s3-bucket-name'
export SSL_VERIFY='True'  # Set to 'False' to disable TLS certificate verification
export DIRECTORY_TO_WATCH='/path/to/directory' # Set to the directory which you want the S3 Data Sweeper to watch for new files
```

Run the script
```bash
python3 watch-and-upload.py
```