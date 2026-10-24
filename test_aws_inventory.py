"""Tests for aws_inventory.py using moto, which fakes AWS locally.
No AWS account or credentials are needed, and nothing is charged.

Run with:  python -m pytest -q
"""

import os

import boto3
from moto import mock_aws

import aws_inventory

# Fake credentials so boto3 never touches a real account
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-2")


@mock_aws
def test_lists_buckets_with_region():
    s3 = boto3.client("s3", region_name="eu-west-2")
    s3.create_bucket(
        Bucket="jb-study-notes",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )
    buckets = aws_inventory.list_buckets(s3)
    assert buckets[0]["name"] == "jb-study-notes"
    assert buckets[0]["region"] == "eu-west-2"


@mock_aws
def test_lists_instances_with_name_tag():
    ec2 = boto3.client("ec2", region_name="eu-west-2")
    image_id = ec2.describe_images()["Images"][0]["ImageId"]
    ec2.run_instances(
        ImageId=image_id, InstanceType="t3.micro", MinCount=1, MaxCount=1,
        TagSpecifications=[{"ResourceType": "instance",
                            "Tags": [{"Key": "Name", "Value": "web-01"}]}],
    )
    instances = aws_inventory.list_instances(ec2)
    assert instances[0]["name"] == "web-01"
    assert instances[0]["state"] == "running"


def test_report_warns_about_running_instances():
    report = aws_inventory.build_report(
        "eu-west-2", [],
        [{"id": "i-123", "name": "web-01", "type": "t3.micro",
          "state": "running", "az": "eu-west-2a"}],
    )
    assert any("cost money" in line for line in report)
