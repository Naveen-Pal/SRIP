# SRIP Portal

This is the SRIP Portal project developed using Flask. It provides facilities for managing interns, faculty, and projects.

## Features

- Admin can add new faculty.
- Faculty can add projects.
- Interns can submit application forms.
- Faculty can shortlist interns and allocate funds.
- Coordinators can send emails to selected interns.
- Interns can submit reports and diaries.

## Setup

1. Install the required packages using `pip install -r requirements.txt`.
2. Run the application using `python run.py`.


Additional
(store in cluster)
```bash
kubectl create secret generic srip-secrets \
  --from-literal=database-url=mysql://user:pass@db-host:3306/srip \
  --from-literal=secret-key=your-secret-key
```

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=your-github-username \
  --docker-password=ghp_yourPATtoken
```