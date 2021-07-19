import io
import json
import logging
from typing import Tuple

import grpc
import boto3
import numpy as np

from PIL import Image
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

from tensorflow.core.framework import tensor_pb2
from tensorflow.core.framework import types_pb2
from tensorflow.core.framework import tensor_shape_pb2

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

session = boto3.Session()
s3_client = session.client('s3')

MODEL_NAME = 'imagenet-resnet50'

_NP_TO_PB_DTYPE = {
    np.uint8: types_pb2.DT_UINT8,
    np.float32: types_pb2.DT_FLOAT,
    np.float64: types_pb2.DT_DOUBLE,
}


def make_tensor_proto(nparray: np.ndarray) -> tensor_pb2.TensorProto:
    assert isinstance(
        nparray, np.ndarray), f'Invalid data type: {type(nparray)}'

    dtype = _NP_TO_PB_DTYPE[nparray.dtype.type]
    dim = [tensor_shape_pb2.TensorShapeProto.Dim(size=i)
           for i in nparray.shape]
    tensor_shape = tensor_shape_pb2.TensorShapeProto(dim=dim)
    tensor_content = nparray.tobytes()
    tensor_proto = tensor_pb2.TensorProto(
        dtype=dtype, tensor_shape=tensor_shape, tensor_content=tensor_content)
    return tensor_proto


def handler(serialized_data, context):
    data = json.loads(serialized_data.read().decode('utf-8'))
    images = preprocess(data)

    server = f'localhost:{context.grpc_port}'
    with grpc.insecure_channel(server) as channel:
        stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
        request = predict_pb2.PredictRequest()
        request.model_spec.name = MODEL_NAME
        request.model_spec.signature_name = 'serving_default'
        images_tensor_proto = make_tensor_proto(images)
        request.inputs['images'].CopyFrom(images_tensor_proto)
        response = stub.Predict(request, 20.0)
    return postprocess(response)


def preprocess(data: dict) -> np.ndarray:
    s3_object = s3_client.get_object(
        Bucket=data['bucket'], Key=data['s3_key'])
    image_data = io.BytesIO(s3_object['Body'].read())
    image = Image.open(image_data).convert('RGB')
    images = np.expand_dims(np.array(image), axis=0)

    return images


def postprocess(data: predict_pb2.PredictResponse) -> Tuple[str, str]:
    result = {}
    for key, value in data.outputs.items():
        if value.dtype == types_pb2.DT_FLOAT:
            val = np.array(value.float_val)
        elif value.dtype == types_pb2.DT_STRING:
            val = np.array(value.string_val).astype(str)
        else:
            continue

        result[key] = val.reshape(
            [dim.size for dim in value.tensor_shape.dim]).tolist()

    result['model_version'] = int(data.model_spec.version.value)
    response_content_type = 'application/json'

    return json.dumps(result), response_content_type
