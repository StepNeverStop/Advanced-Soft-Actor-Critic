# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: replay.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import ndarray_pb2 as ndarray__pb2
import pingpong_pb2 as pingpong__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='replay.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x0creplay.proto\x1a\rndarray.proto\x1a\x0epingpong.proto\"\xe0\x01\n\nAddRequest\x12\x1e\n\x0cn_obses_list\x18\x01 \x03(\x0b\x32\x08.NDarray\x12\x1b\n\tn_actions\x18\x02 \x01(\x0b\x32\x08.NDarray\x12\x1b\n\tn_rewards\x18\x03 \x01(\x0b\x32\x08.NDarray\x12\x1f\n\rnext_obs_list\x18\x04 \x03(\x0b\x32\x08.NDarray\x12\x19\n\x07n_dones\x18\x05 \x01(\x0b\x32\x08.NDarray\x12\x1c\n\nn_mu_probs\x18\x06 \x01(\x0b\x32\x08.NDarray\x12\x1e\n\x0cn_rnn_states\x18\x07 \x01(\x0b\x32\x08.NDarray\"\xab\x02\n\x0bSampledData\x12\x1a\n\x08pointers\x18\x01 \x01(\x0b\x32\x08.NDarray\x12\x1e\n\x0cn_obses_list\x18\x02 \x03(\x0b\x32\x08.NDarray\x12\x1b\n\tn_actions\x18\x03 \x01(\x0b\x32\x08.NDarray\x12\x1b\n\tn_rewards\x18\x04 \x01(\x0b\x32\x08.NDarray\x12\x1f\n\rnext_obs_list\x18\x05 \x03(\x0b\x32\x08.NDarray\x12\x19\n\x07n_dones\x18\x06 \x01(\x0b\x32\x08.NDarray\x12\x1c\n\nn_mu_probs\x18\x07 \x01(\x0b\x32\x08.NDarray\x12\x1b\n\trnn_state\x18\x08 \x01(\x0b\x32\x08.NDarray\x12\x1d\n\x0bpriority_is\x18\t \x01(\x0b\x32\x08.NDarray\x12\x10\n\x08has_data\x18\n \x01(\x08\"N\n\x14UpdateTDErrorRequest\x12\x1a\n\x08pointers\x18\x01 \x01(\x0b\x32\x08.NDarray\x12\x1a\n\x08td_error\x18\x02 \x01(\x0b\x32\x08.NDarray\"[\n\x18UpdateTransitionsRequest\x12\x1a\n\x08pointers\x18\x01 \x01(\x0b\x32\x08.NDarray\x12\x0b\n\x03key\x18\x02 \x01(\t\x12\x16\n\x04\x64\x61ta\x18\x03 \x01(\x0b\x32\x08.NDarray2\xed\x01\n\rReplayService\x12\x1f\n\x0bPersistence\x12\x05.Ping\x1a\x05.Pong(\x01\x30\x01\x12\x1a\n\x03\x41\x64\x64\x12\x0b.AddRequest\x1a\x06.Empty\x12\x1e\n\x06Sample\x12\x06.Empty\x1a\x0c.SampledData\x12.\n\rUpdateTDError\x12\x15.UpdateTDErrorRequest\x1a\x06.Empty\x12\x36\n\x11UpdateTransitions\x12\x19.UpdateTransitionsRequest\x1a\x06.Empty\x12\x17\n\x05\x43lear\x12\x06.Empty\x1a\x06.Emptyb\x06proto3')
  ,
  dependencies=[ndarray__pb2.DESCRIPTOR,pingpong__pb2.DESCRIPTOR,])




_ADDREQUEST = _descriptor.Descriptor(
  name='AddRequest',
  full_name='AddRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='n_obses_list', full_name='AddRequest.n_obses_list', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_actions', full_name='AddRequest.n_actions', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_rewards', full_name='AddRequest.n_rewards', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='next_obs_list', full_name='AddRequest.next_obs_list', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_dones', full_name='AddRequest.n_dones', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_mu_probs', full_name='AddRequest.n_mu_probs', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_rnn_states', full_name='AddRequest.n_rnn_states', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=48,
  serialized_end=272,
)


_SAMPLEDDATA = _descriptor.Descriptor(
  name='SampledData',
  full_name='SampledData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pointers', full_name='SampledData.pointers', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_obses_list', full_name='SampledData.n_obses_list', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_actions', full_name='SampledData.n_actions', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_rewards', full_name='SampledData.n_rewards', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='next_obs_list', full_name='SampledData.next_obs_list', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_dones', full_name='SampledData.n_dones', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='n_mu_probs', full_name='SampledData.n_mu_probs', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='rnn_state', full_name='SampledData.rnn_state', index=7,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='priority_is', full_name='SampledData.priority_is', index=8,
      number=9, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='has_data', full_name='SampledData.has_data', index=9,
      number=10, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=275,
  serialized_end=574,
)


_UPDATETDERRORREQUEST = _descriptor.Descriptor(
  name='UpdateTDErrorRequest',
  full_name='UpdateTDErrorRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pointers', full_name='UpdateTDErrorRequest.pointers', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='td_error', full_name='UpdateTDErrorRequest.td_error', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=576,
  serialized_end=654,
)


_UPDATETRANSITIONSREQUEST = _descriptor.Descriptor(
  name='UpdateTransitionsRequest',
  full_name='UpdateTransitionsRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pointers', full_name='UpdateTransitionsRequest.pointers', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='key', full_name='UpdateTransitionsRequest.key', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data', full_name='UpdateTransitionsRequest.data', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=656,
  serialized_end=747,
)

_ADDREQUEST.fields_by_name['n_obses_list'].message_type = ndarray__pb2._NDARRAY
_ADDREQUEST.fields_by_name['n_actions'].message_type = ndarray__pb2._NDARRAY
_ADDREQUEST.fields_by_name['n_rewards'].message_type = ndarray__pb2._NDARRAY
_ADDREQUEST.fields_by_name['next_obs_list'].message_type = ndarray__pb2._NDARRAY
_ADDREQUEST.fields_by_name['n_dones'].message_type = ndarray__pb2._NDARRAY
_ADDREQUEST.fields_by_name['n_mu_probs'].message_type = ndarray__pb2._NDARRAY
_ADDREQUEST.fields_by_name['n_rnn_states'].message_type = ndarray__pb2._NDARRAY
_SAMPLEDDATA.fields_by_name['pointers'].message_type = ndarray__pb2._NDARRAY
_SAMPLEDDATA.fields_by_name['n_obses_list'].message_type = ndarray__pb2._NDARRAY
_SAMPLEDDATA.fields_by_name['n_actions'].message_type = ndarray__pb2._NDARRAY
_SAMPLEDDATA.fields_by_name['n_rewards'].message_type = ndarray__pb2._NDARRAY
_SAMPLEDDATA.fields_by_name['next_obs_list'].message_type = ndarray__pb2._NDARRAY
_SAMPLEDDATA.fields_by_name['n_dones'].message_type = ndarray__pb2._NDARRAY
_SAMPLEDDATA.fields_by_name['n_mu_probs'].message_type = ndarray__pb2._NDARRAY
_SAMPLEDDATA.fields_by_name['rnn_state'].message_type = ndarray__pb2._NDARRAY
_SAMPLEDDATA.fields_by_name['priority_is'].message_type = ndarray__pb2._NDARRAY
_UPDATETDERRORREQUEST.fields_by_name['pointers'].message_type = ndarray__pb2._NDARRAY
_UPDATETDERRORREQUEST.fields_by_name['td_error'].message_type = ndarray__pb2._NDARRAY
_UPDATETRANSITIONSREQUEST.fields_by_name['pointers'].message_type = ndarray__pb2._NDARRAY
_UPDATETRANSITIONSREQUEST.fields_by_name['data'].message_type = ndarray__pb2._NDARRAY
DESCRIPTOR.message_types_by_name['AddRequest'] = _ADDREQUEST
DESCRIPTOR.message_types_by_name['SampledData'] = _SAMPLEDDATA
DESCRIPTOR.message_types_by_name['UpdateTDErrorRequest'] = _UPDATETDERRORREQUEST
DESCRIPTOR.message_types_by_name['UpdateTransitionsRequest'] = _UPDATETRANSITIONSREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

AddRequest = _reflection.GeneratedProtocolMessageType('AddRequest', (_message.Message,), {
  'DESCRIPTOR' : _ADDREQUEST,
  '__module__' : 'replay_pb2'
  # @@protoc_insertion_point(class_scope:AddRequest)
  })
_sym_db.RegisterMessage(AddRequest)

SampledData = _reflection.GeneratedProtocolMessageType('SampledData', (_message.Message,), {
  'DESCRIPTOR' : _SAMPLEDDATA,
  '__module__' : 'replay_pb2'
  # @@protoc_insertion_point(class_scope:SampledData)
  })
_sym_db.RegisterMessage(SampledData)

UpdateTDErrorRequest = _reflection.GeneratedProtocolMessageType('UpdateTDErrorRequest', (_message.Message,), {
  'DESCRIPTOR' : _UPDATETDERRORREQUEST,
  '__module__' : 'replay_pb2'
  # @@protoc_insertion_point(class_scope:UpdateTDErrorRequest)
  })
_sym_db.RegisterMessage(UpdateTDErrorRequest)

UpdateTransitionsRequest = _reflection.GeneratedProtocolMessageType('UpdateTransitionsRequest', (_message.Message,), {
  'DESCRIPTOR' : _UPDATETRANSITIONSREQUEST,
  '__module__' : 'replay_pb2'
  # @@protoc_insertion_point(class_scope:UpdateTransitionsRequest)
  })
_sym_db.RegisterMessage(UpdateTransitionsRequest)



_REPLAYSERVICE = _descriptor.ServiceDescriptor(
  name='ReplayService',
  full_name='ReplayService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=750,
  serialized_end=987,
  methods=[
  _descriptor.MethodDescriptor(
    name='Persistence',
    full_name='ReplayService.Persistence',
    index=0,
    containing_service=None,
    input_type=pingpong__pb2._PING,
    output_type=pingpong__pb2._PONG,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Add',
    full_name='ReplayService.Add',
    index=1,
    containing_service=None,
    input_type=_ADDREQUEST,
    output_type=ndarray__pb2._EMPTY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Sample',
    full_name='ReplayService.Sample',
    index=2,
    containing_service=None,
    input_type=ndarray__pb2._EMPTY,
    output_type=_SAMPLEDDATA,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='UpdateTDError',
    full_name='ReplayService.UpdateTDError',
    index=3,
    containing_service=None,
    input_type=_UPDATETDERRORREQUEST,
    output_type=ndarray__pb2._EMPTY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='UpdateTransitions',
    full_name='ReplayService.UpdateTransitions',
    index=4,
    containing_service=None,
    input_type=_UPDATETRANSITIONSREQUEST,
    output_type=ndarray__pb2._EMPTY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Clear',
    full_name='ReplayService.Clear',
    index=5,
    containing_service=None,
    input_type=ndarray__pb2._EMPTY,
    output_type=ndarray__pb2._EMPTY,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_REPLAYSERVICE)

DESCRIPTOR.services_by_name['ReplayService'] = _REPLAYSERVICE

# @@protoc_insertion_point(module_scope)
