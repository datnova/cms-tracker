# cms-tracker

##  Install requirements
```console
foo@bar:~$ pip install -r requirements
```

## Run
```
foo@bar:~$ python main.py
```

## Convert pt to onnx
```console
foo@bar:~$ yolo export model=yolov8s.pt format=onnx optimize=True half=True simplify=True
```

video sample:

- `rtsp://192.168.1.105:554/user=admin&password=&channel=1&stream=0.sdp?`
- `rtsp://192.168.1.105:554/user=admin&password=&channel=2&stream=0.sdp?`
- `rtsp://rtspstream:a748730f2a4fe7d4ade26ffb15052972@zephyr.rtsp.stream/pattern`
- `rtsp://rtsp-test-server.viomic.com:554/stream`
- `http://61.211.241.239/nphMotionJpeg?Resolution=320x240&Quality=Standard`
- `http://220.254.72.200/nphMotionJpeg?Resolution=640x640&Quality=Standard`
- `http://210.153.161.125:50000/nphMotionJpeg?Resolution=640x640&Quality=Standard`
- `http://79.3.196.235/nphMotionJpeg?Resolution=640x640&Quality=Standard`
- `http://79.78.158.102/nphMotionJpeg?Resolution=640x640&Quality=Standard`
- `http://115.179.100.76:8080/nphMotionJpeg?Resolution=640x640&Quality=Standard`
- `rtsp://113.165.166.204/1/h264major`
