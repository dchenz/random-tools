# random-tools

Tools created for specific purpose and might be useful in the future.

``azblob.py``

Uploads directories into Azure blob storage since their web UI does not support this. I mainly use it to sync React builds with the ``$web`` static website container in Azure and delete unnecessary files not present in the build.

```
# View files in container
azblob.py ACCOUNT_NAME CONTAINER_NAME

# Note: ~/.azblobrc needs to be configured with a valid SAS token
#       with sufficient permissions at account or container level
#       otherwise the command will fail.
#       Cache in ~/.cache/azblob needs to be deleted if this happens.

# Upload directory files (not including "build" directory)
azblob.py ACCOUNT_NAME CONTAINER_NAME --target build

# Same as above, but it deletes any container file not in "build"
# Unless the flag is used, it will ask you to confirm the action
azblob.py ACCOUNT_NAME CONTAINER_NAME --target build --replace
azblob.py ACCOUNT_NAME CONTAINER_NAME --target build --replace --no-warn

# By default, it won't upload files that haven't changed since last run
azblob.py ACCOUNT_NAME CONTAINER_NAME --target build --no-cache
```

``gitscan.sh``

Switches to every commit in every branch and uses ``grep`` to find string patterns, e.g. accidental commits of app secrets (not that i've done this...).

```
gitscan.sh REGEX_PATTERN
```

``traingame``

Given 4 digits and a set of allowed arithmetic operations, find all expressions where it evaluates to 10.

```
python3 traingame.py 1234 --target 10 --operators "+-*/^"

# Doesn't support --operators and power operator
go run main.go --target 10 --digits 1234
```