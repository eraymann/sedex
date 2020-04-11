# SEDEX Messagebox Manager

## Purpose
This module simplifies the management of your message boxes with asynchronous data exchange via SEDEX.
https://www.bfs.admin.ch/bfs/de/home/register/personenregister/sedex/asynchron.html


You can search your inbox for specific message types or receiving times, clean up your inbox or send messages.
All this with a few simple lines of Python.

This module never interferes with the SEDEX core functionality of secure data transmission but simplifies the management of in- and outbox.

## Get started
``pip install sedex``

That's it.

## Examples
```python
import datetime

from sedex import semebo

# create our instance once by specifying in- and outbox.
messagebox = semebo.MessageBox(inbox=r"C:\sedex\inbox", outbox=r"C:\sedex\outbox")

# list data files, sender ID and message type of all messages in inbox received within the last 24h
for message in messagebox.scan_inbox(from_date=datetime.datetime.now() - datetime.timedelta(hours=24)):
    print(message.data_file,
          message.envelope.sender_id,
          message.envelope.message_type)

# send message
data = r"C:\delivery\ready_to_ship"
transfer_id, envelope = messagebox.send_data(data_dir=data, recipient_id="CH1848", sender_id="Z!1819", message_type=1819)
print(transfer_id,
      envelope.message_id,
      envelope.message_date)

# list candidates older than a week to preview cleanup
messagebox.purge_inbox(older_than_days=7, dry_run=True)

```