"""A class for approving and bonusing mTurk workers.

Example usage:

from compensation import Compensator
comp = Compensator()
for i, row in participant_dataframe.iterrows():
    comp.approve(row.assignment_id)
    comp.grant_bonus(row.worker_id, row.assignment_id, round(row.bonus, 2))

http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_OperationsArticle.html
"""

import os


class Compensator(object):
    """Tools for compensating MTurk workers."""
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, verbose=1,
                 use_sandbox=False, stdout_log=False, verify_mturk_ssl=True):

        self.verbose = verbose
        if aws_access_key_id is None:
            try:
                aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
            except ValueError:
                raise ValueError('You must specify aws_access_key_id or '
                                 'have an environment varibale AWS_ACCESS_KEY_ID')
        if aws_secret_access_key is None:
            try:
                aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
            except ValueError:
                raise ValueError('You must specify aws_secret_access_key or '
                                 'have an environment varibale AWS_ACCESS_KEY_ID')

        self.conn = MechanicalTurk({
            'use_sandbox': use_sandbox,
            'stdout_log': stdout_log,
            'verify_mturk_ssl': verify_mturk_ssl,
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
        })

    def get_status(self, assignment_id):
        """Assignment status, one of Accepted, Rejected, Submitted"""
        r = self.conn.request('GetAssignment',
            AssignmentId=assignment_id,
           )
        status = r.lookup('AssignmentStatus')
        if status:
            return status
        return r
        
    def get_bonus(self, assignment_id):
        """Ammount the worker has already been bonused."""
        r = self.conn.request('GetBonusPayments',
                         AssignmentId=assignment_id)
        if int(r.lookup('NumResults')) == 0:
            return None
        return float(r.lookup('Amount'))

    def approve(self, assignment_id):
        """Approve an assignment.

        Returns response only if there is an error."""
        r = self.conn.request('ApproveAssignment',
                         AssignmentId=assignment_id)
        if r.valid:
            self._log(2, 'Approved assignment {}'.format(assignment_id))
        elif r.lookup('CurrentState') == 'Approved':
            self._log(2, 'Already approved {}'.format(assignment_id))
        else:
            self._log(1, 'Error approving {}'.format(assignment_id))
            return r

    def grant_bonus(self, worker_id, assignment_id, bonus, repeat=False):
        """Grant a bonus for an assignment.

        If repeat is False, no action will be taken if assignment has 
        already been bonused. Returns response only if there if an error.
        """
        if not repeat:
            previous = self.conn.request('GetBonusPayments',
                                    AssignmentId=assignment_id)
            if int(previous.lookup('NumResults')) > 0:
                self._log(2, 'Skipping previously bonused worker {}'.format(worker_id))
                return
        r = self.conn.request('GrantBonus',
                         WorkerId=worker_id,
                         AssignmentId=assignment_id,
                         BonusAmount={'Amount': bonus, 'CurrencyCode': 'USD'},
                         Reason='Performance bonus')
        if r.valid:
            self._log(2, 'Bonused ${} to worker {}'.format(bonus, worker_id))
        else:
            self._log(1, 'Error assigning bonus {} to worker {}, assignment {}'
                     .format(bonus, worker_id, assignment_id))
            return r

    def process_df(self, df):
        df.assignment_id.apply(self.approve)
        for i, row in df.iterrows():
            self.approve(row.assignment_id)
            self.grant_bonus(row.worker_id, row.assignment_id, row.bonus)

    def _log(self, verb, *msg):
        if self.verbose >= verb:
            print('Compensator:', *msg)


# ============================================= #
# ========= Mechanical Turk interface ========= #
# ============================================= #

# This is a slightly modified version of 
#   https://github.com/ctrlcctrlv/mturk-python
# I include it here so that this single file can be distributed.

import time
import hmac
import hashlib
import base64
import json
import requests
import logging
import xmltodict
import collections
import six
from six.moves import range


class MechanicalTurk(object):
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, verbose=1,
                 sandbox=False, stdout_log=False, verify_mturk_ssl=True,
                 request_retry_timeout=10, max_request_retries=5):
        """
        Use mturk_config_file to set config dictionary.
        Update the config dictionary with values from mturk_config_dict (if present).
        """
        self.verbose = verbose
        if aws_access_key_id is None:
            try:
                aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
            except ValueError:
                raise ValueError('You must specify aws_access_key_id or '
                                 'have an environment varibale AWS_ACCESS_KEY_ID')
        if aws_secret_access_key is None:
            try:
                aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
            except ValueError:
                raise ValueError('You must specify aws_secret_access_key or '
                                 'have an environment varibale AWS_ACCESS_KEY_ID')

        # TODO: load from config file

        self.sandbox = sandbox
        self.verify_mturk_ssl = verify_mturk_ssl
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.request_retry_timeout = request_retry_timeout
        self.max_request_retries = max_request_retries

    def _generate_timestamp(self, gmtime):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", gmtime)

    def _generate_signature_python2(self, operation, timestamp, secret_access_key):
        my_sha_hmac = hmac.new(secret_access_key, 'AWSMechanicalTurkRequester' + operation + timestamp, hashlib.sha1)
        my_b64_hmac_digest = base64.encodestring(my_sha_hmac.digest()).strip()
        return my_b64_hmac_digest

    def _generate_signature_python3(self, operation, timestamp, secret_access_key):
        key = bytearray(secret_access_key, 'utf-8')
        msg = bytearray('AWSMechanicalTurkRequester' + operation + timestamp, 'utf-8')
        my_sha_hmac = hmac.new(key, msg, hashlib.sha1)
        my_b64_hmac_digest = base64.encodebytes(my_sha_hmac.digest()).strip()
        return str(my_b64_hmac_digest, 'utf-8')

    def _generate_signature(self, operation, timestamp, secret_access_key):
        if six.PY2:
            return self._generate_signature_python2(operation, timestamp, secret_access_key)
        elif six.PY3:
            return self._generate_signature_python3(operation, timestamp, secret_access_key)

    def _flatten(self, obj, inner=False):
        if isinstance(obj, collections.Mapping):
            if inner: obj.update({'':''})
            iterable = obj.items()
        elif isinstance(obj, collections.Iterable) and not isinstance(obj, six.string_types):
            iterable = enumerate(obj, start=1)
        else:
            return {"": obj}

        rv = {}
        for key, value in iterable:
            for inner_key, inner_value in self._flatten(value, inner=True).items():
                if inner_value != '':
                    rv.update({("{}.{}" if inner_key else "{}{}").format(key, inner_key): inner_value})
        return rv

    def request(self, operation, **request_parameters):
        """Create a Mechanical Turk client request. Unlike other libraries
        (thankfully), my help ends here. You can pass the operation (view the
        list here: http://docs.amazonwebservices.com/AWSMechTurk/latest/AWSMtu
        rkAPI/ApiReference_OperationsArticle.html) as parameter one, and a
        dictionary of arguments as parameter two. To send multiple of the same
        argument (for instance, multiple workers to notify in NotifyWorkers),
        you can send a list."""
        
        if request_parameters is None:
            request_parameters = {}
        self.operation = operation

        if self.sandbox:
            self.service_url='https://mechanicalturk.sandbox.amazonaws.com/?Service=AWSMechanicalTurkRequester'
        else:
            self.service_url='https://mechanicalturk.amazonaws.com/?Service=AWSMechanicalTurkRequester'
        # create the operation signature
        timestamp = self._generate_timestamp(time.gmtime())
        signature = self._generate_signature(operation, timestamp, self.aws_secret_access_key)

        # Add common parameters to request dict
        request_parameters.update({"Operation":operation,"Version":"2014-08-15","AWSAccessKeyId":self.aws_access_key_id,"Signature":signature,"Timestamp":timestamp})

        self.flattened_parameters = self._flatten(request_parameters)

        # Retry request in case of ConnectionError
        req_retry_timeout = self.request_retry_timeout
        for i in range(self.max_request_retries):
            try:
                request = requests.post(self.service_url, params=self.flattened_parameters, verify=self.verify_mturk_ssl)
            except requests.exceptions.ConnectionError as e:
                last_requests_exception = e
                time.sleep(req_retry_timeout)
                req_retry_timeout *= 2
                continue
            break
        else:
            raise last_requests_exception

        request.encoding = 'utf-8'
        xml = request.text # Store XML response, might need it
        response = xmltodict.parse(xml.encode('utf-8'), dict_constructor=dict)
        return MechanicalTurkResponse(response, xml=xml)
    
    def external_form_action(self):
        """Return URL to use in the External question and HTML question form submit action."""
        if self.sandbox:
            return 'https://workersandbox.mturk.com/mturk/externalSubmit'
        else:
            return 'https://www.mturk.com/mturk/externalSubmit'

class MechanicalTurkResponse(dict):
    def __init__(self, response, xml=None):
        dict.__init__(self, response)
        self.response = response
        self.xml = xml
        req = self.lookup("Request")
        self.valid = req.get("IsValid") == "True" if req else False

    # @staticmethod
    # def shorten(r):
    #     assert len(r) == 1
    #     r1 = r[name + 'Response']
    #     r1.pop('OperationRequest')
    #     assert len(r1) == 1
    #     return r1.popitem()[1]

    def _find_item(self, obj, key):
        if isinstance(obj, list):
            for x in obj:
                yield from self._find_item(x, key)
        elif isinstance(obj, dict):
            if set(obj.keys()) == {'Key', 'Value'}:
                if obj['Key'] == key:
                    yield obj['Value']
            if key in obj:
                yield obj[key]

            for k, v in obj.items():
                yield from self._find_item(v, key)


    def lookup(self, element):
        return next(self._find_item(self.response, element), None)


# ========================================= #
# ========= Commandline interface ========= #
# ========================================= #

def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    import pandas as pd

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Approves assignments and gives bonuses on mturk.',
        epilog='''
            For information on AWS acces keys, see
            docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
        '''
    )
    parser.add_argument(
        'csv',
        help='csv file with columns worker_id, assignment_id, bonus'
    )
    parser.add_argument(
        '--id', 
        dest='aws_access_key_id',
    )
    parser.add_argument(
        '--secret',
        # help='AWS_SECRET_ACCESS_KEY',
        dest='aws_secret_access_key',
    )
    parser.add_argument(
        '--verbose',
        default=2,
        type=int,
        help='2=log all actions;  1=log errors only;  0=no logging',
    )

    args = vars(parser.parse_args())
    df = pd.read_csv(args.pop('csv'))

    for col in ('worker_id', 'assignment_id', 'bonus'):
        if col not in df:
            print('Error: csv has no column "{}."'.format(col))
            exit(1)

    comp = Compensator(**args)
    for i, row in df.iterrows():
        comp.approve(row.assignment_id)
        if row.bonus > 0:
            comp.grant_bonus(row.worker_id, row.assignment_id, round(row.bonus, 2))

if __name__ == '__main__':
    main()
