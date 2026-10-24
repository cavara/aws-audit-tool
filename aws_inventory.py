"""
Project 1 - AWS inventory script
================================
Lists the S3 buckets and EC2 instances in your AWS account and prints a
short report. Read-only: it never creates, changes or deletes anything.

What it practises:
- Python: functions, loops, lists, dictionaries, f-strings, try/except
  (video course chapters 3-11, 18-19 and 28)
- AWS: boto3 (the AWS SDK for Python), S3, EC2, regions and IAM permissions
  (SAA chapters 2-3)

Run it with:
    python aws_inventory.py
    python aws_inventory.py --region eu-west-2 --save report.txt
"""

import argparse
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def list_buckets(s3):
    """Return a list of dictionaries, one per S3 bucket."""
    buckets = []
    response = s3.list_buckets()

    for bucket in response["Buckets"]:
        name = bucket["Name"]

        # get_bucket_location returns None for us-east-1 (an old AWS quirk)
        location = s3.get_bucket_location(Bucket=name)["LocationConstraint"]
        region = location or "us-east-1"

        buckets.append(
            {
                "name": name,
                "region": region,
                "created": bucket["CreationDate"].strftime("%Y-%m-%d"),
            }
        )
    return buckets


def list_instances(ec2):
    """Return a list of dictionaries, one per EC2 instance in this region."""
    instances = []

    # Results can come back in several pages, so use a paginator
    paginator = ec2.get_paginator("describe_instances")
    for page in paginator.paginate():
        for reservation in page["Reservations"]:
            for instance in reservation["Instances"]:
                # The Name tag is optional, so default to "(no name)"
                name = "(no name)"
                for tag in instance.get("Tags", []):
                    if tag["Key"] == "Name":
                        name = tag["Value"]

                instances.append(
                    {
                        "id": instance["InstanceId"],
                        "name": name,
                        "type": instance["InstanceType"],
                        "state": instance["State"]["Name"],
                        "az": instance["Placement"]["AvailabilityZone"],
                    }
                )
    return instances


def build_report(region, buckets, instances):
    """Turn the results into lines of text."""
    lines = []
    lines.append(f"AWS inventory report - {datetime.now():%Y-%m-%d %H:%M}")
    lines.append(f"EC2 region checked: {region}")
    lines.append("")

    lines.append(f"S3 buckets ({len(buckets)}) - S3 lists all regions at once")
    if not buckets:
        lines.append("  none")
    for b in buckets:
        lines.append(f"  {b['name']:<40} {b['region']:<15} created {b['created']}")
    lines.append("")

    lines.append(f"EC2 instances in {region} ({len(instances)})")
    if not instances:
        lines.append("  none")
    for i in instances:
        lines.append(
            f"  {i['id']:<20} {i['name']:<20} {i['type']:<12} {i['state']:<10} {i['az']}"
        )

    running = [i for i in instances if i["state"] == "running"]
    if running:
        lines.append("")
        lines.append(f"Reminder: {len(running)} instance(s) running - these cost money.")
    return lines


def main():
    parser = argparse.ArgumentParser(description="List S3 buckets and EC2 instances.")
    parser.add_argument("--region", default="eu-west-2",
                        help="Region to check for EC2 (default: eu-west-2, London)")
    parser.add_argument("--save", help="Also save the report to this file")
    args = parser.parse_args()

    try:
        s3 = boto3.client("s3")
        ec2 = boto3.client("ec2", region_name=args.region)
        buckets = list_buckets(s3)
        instances = list_instances(ec2)
    except NoCredentialsError:
        print("No AWS credentials found. Run 'aws configure sso' (or 'aws configure') first.")
        return
    except ClientError as error:
        # Usually AccessDenied: your IAM user/role is missing a permission
        print(f"AWS refused the request: {error.response['Error']['Code']}")
        print(error.response["Error"]["Message"])
        return

    report = build_report(args.region, buckets, instances)
    print("\n".join(report))

    if args.save:
        with open(args.save, "w") as f:
            f.write("\n".join(report) + "\n")
        print(f"\nSaved to {args.save}")


if __name__ == "__main__":
    main()
