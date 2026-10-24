# AWS security & cost audit tool (Python + boto3)

A read-only Python tool that reports on an AWS account. Version 1 lists the S3 buckets and EC2 instances and warns about running instances, since those cost money. The stretch goals below grow it into a **security and cost audit**: unencrypted or public buckets, unattached EBS volumes, and instances running in forgotten regions.

**Skills shown:** Python (functions, loops, dictionaries, f-strings, error handling, command-line arguments, unit tests), boto3, IAM permissions, S3, EC2, regions, Git/GitHub.

---

## Step 0 – One-off setup (reused by every later project)

### 0.1 Secure your AWS account
1. Create an AWS account. New accounts get the Free plan with credits: see aws.amazon.com/free.
2. Turn on **MFA for the root user**. After that, only use the root user for account-level tasks.
3. Create a **budget alert**: Billing → Budgets → "Zero spend" or a £5 monthly budget, with email alerts. This is AWS Budgets, from your AI Practitioner revision.
4. Create an **IAM user** for everyday work (IAM → Users → Create user, with console access and the `AdministratorAccess` policy), then sign in as that user and give it **its own MFA**. Use it instead of the root user from now on.
   *(IAM Identity Center is the enterprise option, but it needs AWS Organizations, and on the Free plan joining an organisation stops you earning the extra Free Tier credits. Skip it for now.)*

### 0.2 Install the tools
- Python 3 and VS Code. You already have these from the video course.
- AWS CLI v2: docs.aws.amazon.com/cli → "Install or update the AWS CLI".
- Git, and a free GitHub account.

### 0.3 Connect the CLI to your account
```bash
aws login                  # opens your browser; sign in as your IAM user (region: eu-west-2)
aws sts get-caller-identity   # should print your account ID and IAM user
```
`aws login` (added to the AWS CLI in November 2025) uses your console sign-in, so you don't need long-term access keys. Credentials expire, so run `aws login` again when asked. boto3 picks them up automatically. Keep the AWS CLI and boto3 up to date for this to work.

**Never** create root access keys, and never put any access keys in your code or commit them to GitHub.

---

## Step 1 – Run the project

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python aws_inventory.py                       # EC2 in London (eu-west-2)
python aws_inventory.py --region us-east-1    # another region
python aws_inventory.py --save report.txt     # also save to a file
```

To see something in the report, create one S3 bucket in the console first. It's free while empty. If you launch an EC2 instance, use a t3.micro and **terminate it afterwards**.

## Step 2 – Run the tests (no AWS account needed)

The tests use **moto**, which fakes AWS on your computer:
```bash
python -m pytest -q
```

## Step 3 – Put it on GitHub
```bash
git init
git add .
git commit -m "AWS inventory script with tests"
# create an empty repo called aws-audit-tool on github.com, then:
git remote add origin https://github.com/<you>/aws-audit-tool.git
git push -u origin main
```

---

## Roadmap: from inventory to audit tool (stretch goals)
1. Show whether each bucket has **Block Public Access** and **default encryption** turned on (`get_public_access_block`, `get_bucket_encryption`). This links to SAA Chapter 3.
2. Check **every region** for EC2 instances (`ec2.describe_regions()`), and total the running ones.
3. Save the report as **CSV or JSON**. This covers stage 2 of your Python plan.
4. Add **EBS volumes not attached to any instance**. They cost money, and finding waste like this is a classic cost-optimisation task.
5. Add a **GitHub Actions** workflow that runs the tests on every push. That's CI, and a green tick on the repo.
6. Later, run it on a schedule as a **Lambda** function, emailing the results with SNS.

## What I learned
_(Write 3–5 bullet points here when you finish. Employers read this part.)_
