# Call Server

## install requirements

```
pip install -r requirements.txt
```

## run

```
$ python Serve.py
```

## future

1. PDU mode

   This project send SMS message is useing pure text mode.

   So it is not way to send SMS message in Chinese.

   In the future, maybe we can encode message in PDU mode. But it is not easy to do.

2. requestStack

   Considering that when there are multiple users concurrency requesting,

   The service will not process.

   And when a call fails, the service will not process no longer.

   So we need a stack to record the request.
