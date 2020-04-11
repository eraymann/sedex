# coding=utf-8
import datetime
import glob
import logging
import os
import re
import shutil
import uuid
from xml.dom import minidom


class MessageBox(object):

    def __init__(self, inbox, outbox, logs=None):
        self.inbox = inbox
        self.outbox = outbox
        self.logs = logs

    @staticmethod
    def __parse_xml(xml):
        """Parse envelope xml to Envelope object.

        :param str xml: input xml file path to parse
        :return: Envelope object
        :rtype: Envelope

        """
        dom = minidom.parse(xml)
        e = dom.getElementsByTagNameNS("*", "envelope")
        p = {n.localName: [a.childNodes[0].nodeValue for a in dom.getElementsByTagNameNS("*", n.localName)][0] for n in e[0].childNodes if n.localName}
        return Envelope(
            message_id=p["messageId"],
            message_type=p["messageType"],
            sender_id=p["senderId"],
            recipient_id=p["recipientId"],
            message_date=datetime.datetime.strptime(p["messageDate"], "%Y-%m-%dT%H:%M:%S"),
            message_class=p["messageClass"],
            event_date=datetime.datetime.strptime(p["eventDate"], "%Y-%m-%dT%H:%M:%S"),
        )

    def send_data(self, data_dir, recipient_id, sender_id, message_type, message_class=None, event_date=None):
        """Send content of folder and envelope to outbox.

        :param str data_dir: Folder name with data to transmit
        :param str recipient_id: ID of recipient
        :param str sender_id: ID of sender
        :param int message_type: Message type agreed upon by the corresponding offices
        :param MessageClass message_class: Message class (optional)
        :param datetime.datetime event_date: Date of the event to which the data refer (optional)
        :return: transfer id as uuid and envelope Object
        :rtype: (uuid.UUID, Envelope)
        """

        # Create transfer UUID
        transfer_id = uuid.uuid4()

        # Generate data zip
        shutil.make_archive(self.outbox + os.sep + "data_{transferId}".format(transferId=transfer_id), "zip", data_dir)
        logging.debug("archive created from {}".format(data_dir))

        # create envelope
        envelope = Envelope(message_id=uuid.uuid4(), message_type=message_type, sender_id=sender_id, recipient_id=recipient_id,
                            message_date=datetime.datetime.now(), message_class=message_class, event_date=event_date)

        # Generate envelope xml
        xml = u"""<?xml version="1.0" encoding="UTF-8"?>
<eCH-0090:envelope 
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
xmlns:eCH-0090="http://www.ech.ch/xmlns/eCH-0090/1" 
version="1.0" 
xsi:schemaLocation="http://www.ech.ch/xmlns/eCH-0090/1 http://www.ech.ch/xmlns/eCH-0090/1/eCH-0090-1-0.xsd">
<eCH-0090:messageId>{message_id}</eCH-0090:messageId>
<eCH-0090:messageType>{message_type}</eCH-0090:messageType>
<eCH-0090:messageClass>0</eCH-0090:messageClass>
<eCH-0090:senderId>{senderId}</eCH-0090:senderId>
<eCH-0090:recipientId>{recipientId}</eCH-0090:recipientId>
<eCH-0090:eventDate>{message_date}</eCH-0090:eventDate>
<eCH-0090:messageDate>{event_date}</eCH-0090:messageDate>
</eCH-0090:envelope>""".format(message_id=envelope.message_id, message_type=envelope.message_type,
                               senderId=envelope.sender_id, recipientId=envelope.recipient_id,
                               message_date=envelope.message_date.replace(microsecond=0).isoformat(),
                               event_date=envelope.event_date.replace(microsecond=0).isoformat())

        with open(self.outbox + os.sep + "envl_{transferId}.xml".format(transferId=transfer_id), "w") as f:
            f.writelines(xml)

        logging.debug("envelope with message-ID {} created".format(envelope.message_id))

        return transfer_id, envelope

    def scan_inbox(self, sender_id=None, from_date=datetime.datetime(year=2000, month=1, day=1), to_date=datetime.datetime.now()):
        """Scan inbox for specific senders and times.

        :param str sender_id: ID of sender (optional)
        :param datetime.datetime from_date: Start time of the scan interval (optional)
        :param datetime.datetime to_date: End time of the scan interval (optional)
        :return: List of Message objects that match the scan criteria
        :rtype: list of Message
        """

        logging.debug("scanning sedex inbox {} started".format(self.inbox))
        logging.debug("searching for messages received from {} between {} and {}".format(sender_id,
                                                                                         datetime.datetime.strftime(from_date, "%Y-%m-%d %H:%M:%S"),
                                                                                         datetime.datetime.strftime(to_date, "%Y-%m-%d %H:%M:%S")))

        messages = []
        for xml_file in glob.glob(self.inbox + os.sep + "*.xml"):
            envelope = MessageBox.__parse_xml(xml_file)
            if (envelope.sender_id == sender_id or sender_id is None) and from_date <= envelope.message_date <= to_date:
                prefix, guid, extension = re.split("[_.]+", os.path.basename(xml_file))
                data_file = self.inbox + os.sep + "data_{}.zip".format(guid)
                logging.debug("{} found".format(data_file))
                messages.append(Message(envelope=envelope, xml_file=xml_file, data_file=data_file))
        logging.debug("scanning sedex inbox finished")
        return messages

    def purge_inbox(self, older_than_days=30, sender_id=None, dry_run=False):
        """Method to clean up inbox.

        :param int older_than_days: delta days (optional)
        :param str sender_id: id of sender (optional)
        :param bool dry_run: activate for preview of files before deleting (optional)
        """
        logging.debug("deleting outdated sedex messages started")
        for message in self.scan_inbox(sender_id=sender_id, to_date=datetime.datetime.today() - datetime.timedelta(days=older_than_days)):
            for f in [message.xml_file, message.data_file]:
                if dry_run:
                    logging.warning("dry-run: {} would be deleted".format(f))
                else:
                    try:
                        os.remove(f)
                        logging.debug("{} deleted".format(f))
                    except Exception:
                        logging.warning("{} is outdated but could not be deleted".format(f))
        logging.debug("deleting outdated sedex messages finished")


class Envelope(object):
    def __init__(self, message_id, message_type, sender_id, recipient_id, message_date=None, message_class=None, event_date=None):
        self.message_id = message_id
        self.message_type = message_type
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.message_date = message_date if isinstance(message_date, datetime.datetime) else datetime.datetime.now()
        self.message_class = MessageClass.MESSAGE if message_class is None else message_class
        self.event_date = message_date if event_date is None or not isinstance(event_date, datetime.datetime) else event_date


class Message(object):
    def __init__(self, envelope, xml_file, data_file):
        self.envelope = envelope
        self.xml_file = xml_file
        self.data_file = data_file


class MessageClass(object):
    MESSAGE = 0
    RESPONSE = 1
    RECEIPT = 2
    ERROR = 3
