
### Ikaros


#### 安装

以下以群晖docker安装为例:

群晖docker设置路径

| 文件/文件夹 | 装载路径|
| ---- | ----|
|/volume1/Media |  /media|
|/docker/ikaros |  /ikaros/database|

emby/jellyfin挂载设置说明:

| 群晖路径 | jellyfin-docker| emby套件 |
| ----    | ----| ----|
|/volume1/Media |  /media| 不需要设置 |

#### 刮削配置

群晖内实际刮削目录: `/volume1/Media/Movies`
群晖内实际输出目录: `/volume1/Media/output`

| | 针对emby设置 | 针对jellyfin设置 |
| ----        | ---- |----|
| 刮削目录    | /media/Movies | /media/Movies |  
| 软链接前缀  | /volume1/Media/Movie | /media/Movie |
| 硬链接  | 不需要设置 | 不需要设置 |
| 输出路径    | /media/output | /media/output |

注意:转移同理

#### 致谢

[AV_Data_Capture](https://github.com/yoshiko2/AV_Data_Capture)
