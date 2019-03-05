
Nuvla Deployment Test Data
==========================

This repository contains data and scripts for importing test data to a
Nuvla deployment.

You must have the Nuvla python library installed on your machine:

```sh
pip install nuvla-api
```

Then create the main resources and services with:

```sh
python srvs-creds.py
```

You'll probably need to update the credentials in the file. **Be sure
not to check in your credentials.**

Then create the `data-record` resources with:

```sh
python import-gnss.py
```

You will then have all of the GNSS metadata to work with.
