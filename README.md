
### Ikaros


#### 安装

```sh
docker run -d \
  --name=ikaros \
  -p 12346:12346 \
  -v /path/to/media:/media \
  -v /path/to/data:/ikaros/database \
  --restart unless-stopped \
  suwmlee/ikaros:latest
```

#### 刮削配置-软链接前缀说明

- 文件 __1.mp4__ 的文件地址   `/media/1.mp4`

- docker1将/media文件夹映射为/download  
__1.mp4__ 在docker1内的地址： `/download/1.mp4`
将1.mp4软链接到 `/download/movie/`下
即在docker1里`/download/movie/1.mp4` 指向 `/download/1.mp4`

- docker2将/media文件夹映射为/video/media
__1.mp4__ 在docker2内的地址： `/video/media/1.mp4`
同时存在一个软链接文件 `/video/media/movie/1.mp4` 指向 `/download/1.mp4`
但docker2内没有地址为 __/download/1.mp4__ 的文件，此路径只在docker1内有实际文件

- 如果在docker2要使在docker1创建的软链接文件生效即`/video/media/movie/1.mp4` 指向 `/video/media/1.mp4`，就需要修正docker1里软链接指向地址
即 docker1里创建的软链接指向 `/download/1.mp4` 更改为指向 `/video/media/1.mp4`
所以docker1内刮削目录`/download`,软链接前缀`/video/media`

注意:转移同理

#### 致谢

[AV_Data_Capture](https://github.com/yoshiko2/AV_Data_Capture)
