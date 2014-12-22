from __future__ import absolute_import

import click
from catalyze import cli, client, project
from catalyze.helpers import services, jobs
import os, time, sys
import boto.s3.connection, boto.s3.key
import requests

@cli.group("db")
def db():
    """Import/export databases schemas and contents."""

@db.command("import", short_help = "Imports a file into a database.")
@click.argument("database_label")
@click.argument("filepath", type=click.Path(exists = True))
def cmd_import(database_label, filepath):
    """Imports a file into a chosen database service."""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    service_id = get_service_id(session, settings["environmentId"], database_label)
    if service_id is None:
        print("Service with label '%s' not found" % (database_label,))
    else:
        print("Beginning import of " + filepath)

        print("Requesting credentials...")
        resp = services.initiate_import(session, settings["environmentId"], service_id)

        bucket_name = resp["bucketName"]
        username = resp["userName"]
        s3_access = resp["accessKey"]
        s3_secret = resp["secretKey"]
        s3_token = resp["token"]

        connection = boto.s3.connection.S3Connection(s3_access, s3_secret, security_token = s3_token)
        bucket = connection.get_bucket(bucket_name, validate = False)

        key = boto.s3.key.Key(bucket)
        key.name = os.path.basename(filepath)
        key.metadata["x-amz-server-side-encryption"] = "AES256"
        print("Uploading...")
        with open(filepath, 'rb') as fp:
            key.set_contents_from_file(fp)

        print("Processing import...")
        resp = services.process_import(session, settings["environmentId"], service_id, {
            "bucketName": bucket_name,
            "userName": username
        })
        job_id = resp["jobId"]
        print("Job ID = " + job_id)
        while True:
            job = jobs.retrieve(session, settings["environmentId"], service_id, job_id)
            if job["status"] not in ["scheduled", "started", "running"]:
                if job["status"] == "finished":
                    print("\nImport complete.")
                else:
                    print("\nError - import job ended in status '%s'. Check log for details.")
                break
            sys.stdout.write(".")
            time.sleep(2)


@db.command(short_help = "Exports a database, downloads dump.")
@click.argument("database_label")
def export(database_label):
    """Exports a database and downloads the dump file."""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    service_id = get_service_id(session, settings["environmentId"], database_label)
    if service_id is None:
        print("Service with label '%s' not found" % (database_label,))
    else:
        resp = services.initiate_export(session, settings["environmentId"], service_id)
        job_id = resp["jobId"]
        print("Job ID = %s" % (job_id,))

        while True:
            job = jobs.retrieve(session, settings["environmentId"], service_id, job_id)
            if job["status"] not in ["scheduled", "started", "running"]:
                if job["status"] == "finished":
                    print("\nExport complete, downloading...")
                    download_file(job["spec"]["downloadURL"])
                else:
                    print("\nError - import job ended in status '%s'. Check log for details.")
                break
            sys.stdout.write(".")
            time.sleep(2)

def download_file(url):
    resp = requests.get(url, stream = True)
    filename = None
    if "content-disposition" in resp.headers:
        disposition = resp.headers["content-disposition"]
        filename = disposition[disposition.rfind("filename="):]
    else:
        filename = url.split("/")[-1]
    split_ext = os.path.splitext(filename)
    filename = "%s_%s%s" % (split_ext[0], time.strftime("%Y-%m-%d_%H-%M"), split_ext[1])
    with open(filename, 'wb') as fp:
        for chunk in resp.iter_content(chunk_size = 1024):
            if chunk:
                fp.write(chunk)
    resp.close()
    print("Download complete, saved to %s" % (filename,))
