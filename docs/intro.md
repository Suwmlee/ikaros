
## 使用


刮削配置可参考 [Movie_Data_Capture的wiki](https://github.com/yoshiko2/Movie_Data_Capture/wiki)
~~精力有限，直接用的mdc的刮削库，因设计、需求不同，参数略有增减~~

### 获取刷新emby库地址

刷新emby库部分需要查找emby库刷新地址，[参考](https://emby.media/community/index.php?/topic/50862-trigger-a-library-rescan-via-cmd-line/&do=findComment&comment=487929)

此处需要配图：F12获取库 item 刷新链接

替换地址后半部分为 api_key

组合后就是使用的地址

emby也提供了其他刷新方式，但实现会麻烦很多，有兴趣的可以提交PR

### 自动检测/推送配置

- 配置`transmission`/`qBittorrent`下载完成脚本
  - `scripts`目录下`trcomplete.sh`/`qbcomplete.sh`
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
