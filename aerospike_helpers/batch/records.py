##########################################################################
# Copyright 2013-2022 Aerospike, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##########################################################################

import typing as ty

TypeOps = ty.List[ty.Dict]
TypeBatchPolicyWrite = ty.Union[ty.Dict, None]
TypeBatchPolicyRemove = ty.Union[ty.Dict, None]
TypeBatchPolicyApply = ty.Union[ty.Dict, None]
TypeBatchPolicyRead = ty.Union[ty.Dict, None]
TypeRecord = ty.Union[ty.Tuple, None]
TypeUDFArgs = ty.List[ty.Any]


class _Types:
    READ = 0
    WRITE = 1
    APPLY = 2
    REMOVE = 3


class BatchRecord:
    """ BatchRecord provides the base fields for BatchRecord objects.

        BatchRecord should usually be read from as a result and not created by the user. Its subclasses can be used as
        input to batch_write.
        Client methods :meth:`~Client.batch_apply`, :meth:`~Client.batch_operate`, :meth:`~Client.batch_remove`
        with batch_records field as a list of these BatchRecord objects containing the batch request results.

        Attributes:
            key (:obj:`tuple`): The aerospike key to operate on.
            record (:ref:`aerospike_record_tuple`): The record corresponding to the requested key.
            result (int): The status code of the operation.
            in_doubt (bool): Is it possible that the write transaction completed even though an error was generated. \
            This may be the case when a client error occurs (like timeout) after the command was sent \
            to the server.
    """

    def __init__(self, key: tuple) -> None:
        self.key = key
        self.record = None
        self.result = 0
        self.in_doubt = False


class Write(BatchRecord):
    """ Write is used for executing Batch write operations with batch_write and retrieving batch write results.

        Attributes:
            key (:obj:`tuple`): The aerospike key to operate on.
            record (:obj:`tuple`): The record corresponding to the requested key.
            result (int): The status code of the operation.
            in_doubt (bool): Is it possible that the write transaction completed even though an error was generated. \
            This may be the case when a client error occurs (like timeout) after the command was sent \
            to the server.
            ops (:ref:`aerospike_operation_helpers.operations`): A list of aerospike operation dictionaries to perform
                on the record at key.
            policy (:ref:`aerospike_batch_write_policies`, optional): An optional dictionary of batch write policy
                flags.
    """

    def __init__(
        self, key: tuple, ops: "TypeOps", meta: "dict" = None, policy: "TypeBatchPolicyWrite" = None
    ) -> None:
        """
        Example::

            # Create a batch Write to increment bin "a" by 10 and read the result from the record.
            import aerospike_helpers.operations as op


            bin_name = "a"

            namespace = "test"
            set = "demo"
            user_key = 1
            key = (namespace, set, user_key)

            ops = [
                op.increment(bin_name, 10),
                op.read(bin_name)
            ]

            bw = Write(key, ops)
        """
        super().__init__(key)
        self.ops = ops
        self._type = _Types.WRITE
        self._has_write = True
        self.meta = meta
        self.policy = policy


class Read(BatchRecord):
    """ Read is used for executing Batch read operations with batch_write and retrieving results.

        Attributes:
            key (:obj:`tuple`): The aerospike key to operate on.
            record (:obj:`tuple`): The record corresponding to the requested key.
            result (int): The status code of the operation.
            in_doubt (bool): Is it possible that the write transaction completed even though an error was generated. \
            This may be the case when a client error occurs (like timeout) after the command was sent \
            to the server.
            ops (:ref:`aerospike_operation_helpers.operations`): list of aerospike operation dictionaries to perform on
                the record at key.
            read_all_bins (bool, optional): An optional bool, if True, read all bins in the record.
            policy (:ref:`aerospike_batch_read_policies`, optional): An optional dictionary of batch read policy flags.
    """

    def __init__(
        self,
        key: tuple,
        ops: ty.Union[TypeOps, None],
        read_all_bins: bool = False,
        meta: "dict" = None,
        policy: "TypeBatchPolicyRead" = None,
    ) -> None:
        """
        Example::

            # Create a batch Read to read bin "a" from the record.
            import aerospike_helpers.operations as op


            bin_name = "a"

            namespace = "test"
            set = "demo"
            user_key = 1
            key = (namespace, set, user_key)

            ops = [
                op.read(bin_name)
            ]

            br = Read(key, ops)
        """
        super().__init__(key)
        self.ops = ops
        self.read_all_bins = read_all_bins
        self._type = _Types.READ
        self._has_write = False
        self.meta = meta
        self.policy = policy


class Apply(BatchRecord):
    """ BatchApply is used for executing Batch UDF (user defined function) apply operations with batch_write and
        retrieving results.

        Attributes:
            key (:obj:`tuple`): The aerospike key to operate on.
            module (str): Name of the lua module previously registered with the server.
            function (str): Name of the UDF to invoke.
            args (:obj:`list`): List of arguments to pass to the UDF.
            record (:ref:`aerospike_record_tuple`): The record corresponding to the requested key.
            result (int): The status code of the operation.
            in_doubt (bool): Is it possible that the write transaction completed even though an error was generated. \
            This may be the case when a client error occurs (like timeout) after the command was sent \
            to the server.
            ops (:ref:`aerospike_operation_helpers.operations`): A list of aerospike operation dictionaries to perform
                on the record at key.
            policy (:ref:`aerospike_batch_apply_policies`, optional): An optional dictionary of batch apply policy
                flags.
    """

    def __init__(
        self, key: tuple, module: str, function: str, args: "TypeUDFArgs", policy: "TypeBatchPolicyApply" = None
    ) -> None:
        """
        Example::

            # Create a batch Apply to apply UDF "test_func" to bin "a" from the record.
            # Assume that "test_func" takes a bin name string as an argument.
            # Assume the appropriate UDF module has already been registered.
            import aerospike_helpers.operations as op


            module = "my_lua"
            function = "test_func"

            bin_name = "a"
            args = [
                bin_name
            ]

            namespace = "test"
            set = "demo"
            user_key = 1
            key = (namespace, set, user_key)

            ba = Apply(key, module, function, args)
        """
        super().__init__(key)
        self._type = _Types.APPLY
        self._has_write = True
        self.module = module
        self.function = function
        self.args = args
        self.policy = policy


class Remove(BatchRecord):
    """ Remove is used for executing Batch remove operations with batch_write and retrieving results.

        Attributes:
            key (:obj:`tuple`): The aerospike key to operate on.
            record (:ref:`aerospike_record_tuple`): The record corresponding to the requested key.
            result (int): The status code of the operation.
            in_doubt (bool): Is it possible that the write transaction completed even though an error was generated. \
            This may be the case when a client error occurs (like timeout) after the command was sent \
            to the server.
            ops (:ref:`aerospike_operation_helpers.operations`): A list of aerospike operation dictionaries to perform
                on the record at key.
            policy (:ref:`aerospike_batch_remove_policies`, optional): An optional dictionary of batch remove policy
                flags.
    """

    def __init__(self, key: tuple, policy: "TypeBatchPolicyRemove" = None) -> None:
        """
        Example::

            # Create a batch Remove to remove the record.
            import aerospike_helpers.operations as op


            namespace = "test"
            set = "demo"
            user_key = 1
            key = (namespace, set, user_key)

            br = Remove(key, ops)
        """
        super().__init__(key)
        self._type = _Types.REMOVE
        self._has_write = True
        self.policy = policy


TypeBatchRecordList = ty.List[BatchRecord]


class BatchRecords:
    """ BatchRecords is used as input and output for multiple batch APIs.

        Attributes:
            batch_records (list): A list of BatchRecord subtype objects used to \
            define batch operations and hold results. BatchRecord Types can be Remove, Write, \
            Read, and Apply.
            result (int): The status code of the last batch call that used this BatchRecords.
            0 if all batch subtransactions succeeded (or if the only failures were FILTERED_OUT or RECORD_NOT_FOUND)
            non 0 if an error occured. The most common error being -16 (One or more batch sub transactions failed).
    """

    def __init__(self, batch_records: TypeBatchRecordList = None) -> None:
        """
        Example::

            # Create a BatchRecords to remove a record, write a bin, and read a bin.
            # Assume client is an instantiated and connected aerospike cleint.
            import aerospike_helpers.operations as op


            namespace = "test"
            set = "demo"
            bin_name = "id"
            keys = [
                (namespace, set, 1),
                (namespace, set, 2),
                (namespace, set, 3)
            ]

            brs = BatchRecords(
                [
                    Remove(
                        key=(namespace, set, 1),
                    ),
                    Write(
                        key=(namespace, set, 100),
                        ops=[
                            op.write(bin_name, 100),
                            op.read(bin_name),
                        ]
                    ),
                    BatchRead(
                        key=(namespace, set, 333),
                        ops=[
                            op.read(bin_name)
                        ]
                    )
                ]
            )

            # Note this call will mutate brs and set results in it.
            client.batch_write(brs)
        """

        if batch_records is None:
            batch_records = []

        self.batch_records = batch_records
        self.result = 0
