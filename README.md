
### Ikaros


#### 安装

以下以群晖docker安装为例:

- 设置目录 
![avatar](./src/images/synology_install_1.png)
__注意:__ 选择实际需要刮削/转移的目录
- 设置端口
![avatar](./src/images/synology_install_2.png)


#### 目录设置说明

本项目挂载设置:

| 群晖目录 | 本项目docker内目录|
| ---- | ----|
|/volume1/Media |  /media|

emby套件无需设置挂载目录

jellyfin-docker挂载目录:

| 群晖目录 | jellyfin目录|
| ----    | ----|
|/volume1/Media |  /media|


刮削目录: __/volume1/Media/Movie__
输出目录: __/volume1/Media/ForServer__

| | emby使用 | jellyfin使用 |
| ----        | ---- |----|
| 输入目录    | /media/Movie | /media/Movie |  
| 软链接前缀  | /volume1/Media/Movie | /media/Movie |
| 输出目录    | /media/ForServer | /media/ForServer |


#### 致谢

[AV_Data_Capture](https://github.com/yoshiko2/AV_Data_Capture)
