#  SageMaker Inference Deployment
SageMakerでオリジナルのTensorFlowモデルによる推論エンドポイントをデプロイします。

## 事前準備
```
# モデル生成
$ python model_exporter.py --export_path imagenet-resnet50/<model_version>

# Protoファイルの生成
$ bash build_protobuf.sh

# モデルファイルの作成
$ tar cvfz model.tar.gz imagenet-resnet50 code

# モデルファイルのアップロード
$ aws s3 cp model.tar.gz s3://<bucket_name>/<dir_name>/
```

## デプロイおよび推論
アップロードしたモデルを用い、SageMakerへ推論エンドポイントのデプロイおよび、デプロイしたエンドポイントを使用した画像の推論を行います。
```
$ python main.py \
    --deploy_role_arn arn:aws:iam::<account>:role/<deploy_role> \
    --model_path s3://<bucket_name>/<dir_name>/model.tar.gz \
    --exec_role_arn arn:aws:iam::<account>:role/<sagemaker_exec_role> \
    --tf_version 2.3.1 \
    --model_name imagenet-resnet50 \
    --num_instances 1 \
    --instance_type ml.t2.medium \
    --bucket <target_image_bucket> \
    --s3_key <target_image_key>
```