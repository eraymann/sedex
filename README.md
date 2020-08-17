# SEDEX Messagebox Manager

## Purpose
This module simplifies the management of your message boxes with asynchronous data exchange via [SEDEX](https://www.bfs.admin.ch/bfs/de/home/register/personenregister/sedex/asynchron.html).


You can search your inbox for specific message types or receiving times, clean up your inbox or send messages.
All this with a few simple lines of Python.

This module never interferes with the SEDEX core functionality of secure data transmission but simplifies the management of in- and outbox.

## Install
``pip install sedex``

That's it.

## Examples
### Get started
Create instance by specifying in- and outbox.
```python
from sedex import semebo

messagebox = semebo.MessageBox(inbox=r"C:\sedex\inbox", outbox=r"C:\sedex\outbox")
```

### Search for Messages
Scan your inbox for messages fullfilling secified criteria.
  
Get all messages received _within the last 24h_:
```python
import datetime

for message in messagebox.scan_inbox(
    from_date=datetime.datetime.now() - datetime.timedelta(hours=24)
):
    print(message.data_file,
          message.envelope.sender_id,
          message.envelope.message_type)
```

Get the most recent message with message type _1819_:
```python
message = messagebox.scan_inbox(message_type=1819, latest=True):
print(message.data_file,
      message.envelope.sender_id,
      message.envelope.message_date)
```
### Send Messages
Send the entire content of a folder:
```python
data = r"C:\delivery\ready_to_ship"
transfer_id, envelope = messagebox.send_data(
    file_or_folder=data, 
    recipient_id="CH1848",
    sender_id="Z!1819",
    message_type=1819
)
print(transfer_id,
      envelope.message_id,
      envelope.message_date)
```

### Clean-up Inbox
List candidates older than a week to preview cleanup:
```python
messagebox.purge_inbox(older_than_days=7, dry_run=True)
```