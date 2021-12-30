
## 使用说明

__刮削:__<br>
配置可参考 [Movie_Data_Capture的wiki](https://github.com/yoshiko2/Movie_Data_Capture/wiki)<br>
~~精力有限，直接用的mdc的刮削库，因设计、需求不同，参数略有修改~~

cookies部分，浏览器内获取的完整的cookies内容

刮削默认跳过带有忽略或已完成标记的影片，如果修改了刮削番号/中文标签/分集等，需要将状态设置为未完成并重新刮削

__转移:__<br>
开启`修正剧集名`后，最多两级目录。第一级是`剧集名`，第二级是`季`,分季视频在emby内手动识别一次就可以自动归到一个剧集下。
遇到异常的视频，可参考tmdb内数据，手动调整具体`季/集`编号。

所有修改均在web页面内操作，ikaros会记录。再次更新可以直接使用记录，便于再次刷新与维护


### 获取刷新emby库地址

刷新emby库部分需要查找emby库刷新地址，[参考](https://emby.media/community/index.php?/topic/50862-trigger-a-library-rescan-via-cmd-line/&do=findComment&comment=487929)

按图示操作:

  <!-- ![emby-1](imgs/emby1.jpg) -->
<img src="imgs/emby1.jpg" alt="emby-1" width="600"/>

图 1: 刷新媒体库
  <!-- ![emby-2](imgs/emby2.jpg) -->
<img src="imgs/emby2.jpg" alt="emby-1" width="600"/>

图 2: 查找媒体刷新链接

找到刷新该媒体库的地址:
```
http://192.168.1.233:8096/emby/Items/3227ce1e069754c594af25ea66d69fc7/Refresh?Recursive=true&ImageRefreshMode=Default&MetadataRefreshMode=Default&ReplaceAllImages=false&ReplaceAllMetadata=false&X-Emby-Client=Emby Web&X-Emby-Device-Name=Chrome Windows&X-Emby-Device-Id=123123123214123&X-Emby-Client-Version=4.7.0.19&X-Emby-Token=123123412312312
```

得到媒体库item的ID为:`3227ce1e069754c594af25ea66d69fc7`

在emby服务端`控制面板 - 高级 - API密钥` 获取 __api_key__ : `dd4b16934ab81cbxxxxxx`

替换刷新地址`ReplaceAllMetadata=false`后部分:
```
http://192.168.1.233:8096/emby/Items/3227ce1e069754c594af25ea66d69fc7/Refresh?Recursive=true&ImageRefreshMode=Default&MetadataRefreshMode=Default&ReplaceAllImages=false&ReplaceAllMetadata=false&api_key=dd4b16934ab81cbxxxxxx
```

以上地址即需要填入的刷新库链接地址

~~emby也提供了其他刷新方式，但实现会麻烦很多，有兴趣的可以提交PR~~

### 自动检测/推送配置

- 配置`transmission`/`qBittorrent`下载完成脚本
  - `scripts`目录下`trcomplete.sh`/`qbcomplete.sh`，或在web页面里查看具体脚本内容
  - 在下载软件配置内指定脚本路径即可
- 在`自动`选项内配置过滤目录


__注意:__ 
- 默认请求 __127.0.0.1__ ,需根据实际情况更改
- 参考[配置tr完成脚本](https://github.com/ronggang/transmission-web-control/wiki/About-script-torrent-done-filename)

### 刮削配置-软链接前缀说明

若不确定，可以选择硬链接

|                       | 1.mkv      | 软链接配置      | 软链接文件 | 实际指向地址      | 修正前缀 | 修正后实际指向地址 |
| --------------------- | ---------- | --------------- | ---------- | ----------------- | -------- | ------------------ |
| nas内绝对地址         | /m/1.mkv   | 源目录 `/s/m`   | /o/1.mkv   | /s/m/1.mkv (无效) | `/e/m`   | /e/m/1.mkv (无效)  |
| 刮削docker内绝对地址  | /s/m/1.mkv | 输出目录 `/s/o` | /s/o/1.mkv | /s/m/1.mkv        | ^        | /e/m/1.mkv (无效)  |
| emby-docker内绝对地址 | /e/m/1.mkv | ^               | /e/o/1.mkv | /s/m/1.mkv (无效) | ^        | /e/m/1.mkv         |

__注:__
1. 软链接只在有实际指向文件的环境内生效，适应范围单一
2. 软链接清理只需要删除源文件即可，硬链接需要删除源文件与硬连接后的文件
