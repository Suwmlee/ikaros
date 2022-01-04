
## 使用说明

### 配置

##### 刮削

配置可参考 [Movie_Data_Capture wiki](https://github.com/yoshiko2/Movie_Data_Capture/wiki)<br>
~~精力有限，使用mdc的刮削库，因设计、需求不同，参数略有修改~~

cookies内容: 浏览器内获取的完整的cookies,不需要json格式

刮削默认跳过带有忽略或已完成标记的影片，如果自定义刮削番号/中文标签等，需要将状态设置为未完成并重新刮削

##### 转移

开启`修正剧集名`后，最多两级目录。第一级是`剧名`，第二级是`季`,分季视频在emby内手动识别一次就可以自动归到一个剧集下。
遇到异常的视频，可参考tmdb内数据，手动修改`季/集`编号，并再次进行转移操作。

_请在web页面内进行自定义修改，这样ikaros会更新记录，再次转移会应用修改_<br>
_[媒体文件分类/命名参考](https://suwmlee.github.io/posts/2021/12/05/%E5%AA%92%E4%BD%93%E6%96%87%E4%BB%B6%E5%91%BD%E5%90%8D.html)_<br>
_在命名与网络正常的情况下，emby自带的刮削功能完全可以满足日常使用，即使出现个别问题，也可以手动修改_

### 获取刷新emby库地址

在刮削和转移配置内填入`emby链接`即可在任务完成后刷新emby库

刷新emby需要查找刷新地址，[参考论坛回复](https://emby.media/community/index.php?/topic/50862-trigger-a-library-rescan-via-cmd-line/&do=findComment&comment=487929)

具体按图示操作:

图 1: 网页内刷新媒体库<br>
<img src="imgs/emby1.jpg" alt="emby-1" width="600"/>

图 2: 查找媒体刷新链接<br>
<img src="imgs/emby2.jpg" alt="emby-2" width="600"/>

找到刷新该媒体库的地址:
```
http://192.168.1.233:8096/emby/Items/3227ce1e069754c594af25ea66d69fc7/Refresh?Recursive=true&ImageRefreshMode=Default&MetadataRefreshMode=Default&ReplaceAllImages=false&ReplaceAllMetadata=false&X-Emby-Client=Emby Web&X-Emby-Device-Name=Chrome Windows&X-Emby-Device-Id=123123123214123&X-Emby-Client-Version=4.7.0.19&X-Emby-Token=123123412312312
```

得到媒体库item的ID为:`3227ce1e069754c594af25ea66d69fc7`

在emby服务端`控制面板 - 高级 - API密钥` 获取 __api_key__ : `dd4b16934ab81cbxxxxxx`

替换链接`ReplaceAllMetadata=false`后半部分:
```
http://192.168.1.233:8096/emby/Items/3227ce1e069754c594af25ea66d69fc7/Refresh?Recursive=true&ImageRefreshMode=Default&MetadataRefreshMode=Default&ReplaceAllImages=false&ReplaceAllMetadata=false&api_key=dd4b16934ab81cbxxxxxx
```

以上地址即填入的刷新emby链接

~~emby也提供了其他刷新方式，但实现会麻烦很多，有兴趣的可以提交PR~~

### 关联 transmission/qBittorrent

- 配置 transmission/qBittorrent 下载完成脚本
  - 脚本在项目的`scripts`目录下，或在web页面里查看并自行创建脚本
  - 在下载软件配置内指定脚本路径
- 在`自动`选项内配置过滤目录

__注:__ 
- 默认请求 __127.0.0.1__ ,需根据实际情况更改
- tr可参考[配置完成脚本](https://github.com/ronggang/transmission-web-control/wiki/About-script-torrent-done-filename)

### 软链接前缀说明

若不确定，可以选择硬链接

|               | 1.mkv地址  | ikaros软链接配置 | 软链接后   | 实际指向地址    | 修正前缀 | 修正后指向      |
| ------------- | ---------- | ---------------- | ---------- | --------------- | -------- | --------------- |
| NAS           | /m/1.mkv   | 源目录 `/s/m`    | /o/1.mkv   | /s/m/1.mkv 无效 | -        | /e/m/1.mkv 无效 |
| ikaros-docker | /s/m/1.mkv | 输出目录 `/s/o`  | /s/o/1.mkv | /s/m/1.mkv      | `/e/m`   | /e/m/1.mkv 无效 |
| emby-docker   | /e/m/1.mkv | -                | /e/o/1.mkv | /s/m/1.mkv 无效 | -        | /e/m/1.mkv      |

__注:__
1. 软链接只在有实际指向文件的环境内生效，适应范围单一
2. 软链接清理只需要删除源文件即可，硬链接需要删除源文件与硬连接后的文件
