# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 et

import email.charset
import email.message
import email.header
import email.utils

#class Mail(dict):
#    mail_native = email.message.Message()
#
#    def __init__(self, logger, uid, mail=None):
#        self.logger = logger
#        self.uid = uid
#        self.mail_native = mail
#        self.parse_email_object()
#
#    def parse_email_object(self):
#        fields_to_store = {
#            # TODO store as much as possible, get rid of this static list
#            'content-type': None,
#            'date': None,
#            'delivered-to': {'multiple': True},
#            'from': None,
#            'list-id': None,
#            'message-id': None,
#            'received': {'multiple': True,
#                         'split': True},
#            'return-path': None,
#            'subject': None,
#            'to': None,
#            'user-agent': None,
#            'x-redmine-project': None,
#            'x-redmine-host': None,
#            'x-gitlab-project': None,
#        }
#
#        for field, properties in fields_to_store.items():
#            if type(properties) is dict:
#                if properties.get('multiple', None):
#                    fields = self.mail_native.get_all(field)
#                    if fields is None:
#                        continue
#                    #    self.logger.debug('Unable to parse raw mail with uid=%s: %s %s', self.uid, self.mail_native, field)
#                    #    raise ValueError('Unable to parse raw mail with uid=%s' % (self.uid))
#
#                    if properties.get('split', None):
#                        _fields = []
#                        for f in fields:
#                            _fields.append(f.split('\r\n'))
#                        _fields = fields
#                    self[field] = fields
#                else:
#                    field_value = self.mail_native.get(field)
#                    if field_value:
#                        self[field] = field_value
#            else:
#                field_value = self.mail_native.get(field)
#                if field_value:
#                    self[field] = field_value


class Mail():
    """
    A dict representing a mail
    """

    #def __init__(self, logger, charset='utf-8', mail_native=None, **kwargs):
    def __init__(self, logger, charset='utf-8', headers={}, body={}, mail_native=None):
        self.logger = logger
        self.charset = charset
        self.mail_native = mail_native

        self._headers = headers
        self._body = body

        if mail_native:
            self.__parse_native_mail()

    def clean_value(self, value, encoding):
        """
        Converts value to utf-8 encoding
        """
        if isinstance(value, bytes):
            return value.decode(encoding)
        return value

    def set_header(self, name, value):
        """
        Set mail header
        """
        self._headers[name] = value
        return self._headers

    def get_header(self, name):
        """
        Return mail header by name
        """
        return self._headers.get(name)

    def update_headers(self, headers):
        """
        Update mail headers
        """
        self._headers.update(headers)
        return self._headers

    def get_headers(self):
        """
        Get all mail headers
        """
        return self._headers

    def set_body(self, body):
        """
        Set mail body
        """
        self._body = body
        return self._body

    def get_body(self, name):
        """
        Return mail body by name
        """
        return self._body

    def get_native(self):
        """
        Returns a native (email.message.Message()) object
        """
        if not self.mail_native:
            self.mail_native = email.message.Message()

            email.charset.add_charset(self.charset, email.charset.QP, email.charset.QP)
            c = email.charset.Charset(self.charset)
            self.mail_native.set_charset(c)

            if self.get_header('Message-Id') is None:
                self.set_header('Message-Id', email.utils.make_msgid())

            for field_name, field_value in self.get_headers().items():
                self.mail_native.add_header(field_name, field_value)
        return self.mail_native

    def __parse_native_mail(self):
        """
        Parses a native (email.message.Message()) object
        """
        self._headers = {}
        self._body = None

        if not self.mail_native.is_multipart():
            self.set_body = self.mail_native.get_payload(decode=True).decode('utf-8')
        else:
            self.set_body = self.mail_native.get_payload()

        for field_name in self.mail_native.keys():
            field_value = self.mail_native.get(field_name)

            if field_name in ['Subject', 'From', 'To']:
                if field_name in self._headers.keys():
                    continue
                field_value = email.header.decode_header(self.mail_native.get(field_name))
                field_value = self.clean_value(field_value[0][0], field_value[0][1])
                self._headers[field_name] = field_value
            elif field_name in self._headers.keys():
                self._headers[field_name].append(field_value)
            elif field_name in ['Received']:
                self._headers[field_name] = [field_value]
            else:
                self._headers[field_name] = field_value
