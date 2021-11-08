
# ikaros

关联`transmission`/`qBittorrent`与`emby`，下载任务完成后，自动筛选文件创建软/硬链接，自动刮削JAV目录，推送emby库刷新。

- 批量软/硬链接
- 批量处理文件名，优化剧集命名
- JAV刮削
- 下载完成后脚本
- 自动化任务

#### 安装

本项目仅后端，需要搭配[web端](https://github.com/Suwmlee/ikaros-web)
可自行运行或使用编译好的文件

- 使用编译好的[web  release](https://github.com/Suwmlee/Spike/tree/release)
  1. 将`index.html`文件放到`web/templates`
  2. 将其他文件放到`web/static`
  3. `pip install -r requirements.txt`
  4. `python app.py`

- 使用[docker](https://registry.hub.docker.com/r/suwmlee/ikaros)(推荐)
```sh
docker run -d \
  --name=ikaros \
  -p 12346:12346 \
  -v /path/to/media:/media \
  -v /path/to/data:/ikaros/database \
  -v /path/to/scripts:/ikaros/scripts \
  --restart unless-stopped \
  suwmlee/ikaros:latest
```

- 配置`transmission`/`qBittorrent`下载完成脚本
  - `scripts`目录下`trcomplete.sh`/`trcomplete.sh`
  - 在下载软件配置内指定脚本路径即可
__注意:__ 默认请求 127.0.0.1,需根据实际情况更改

#### 刮削配置-软链接前缀说明

若不确定，可以选择硬链接

|                       | 1.mkv      | 软链接配置 -->  | 软链接文件 | 实际指向地址      | 修正前缀 | 修正后实际指向地址 |
| --------------------- | ---------- | --------------- | ---------- | ----------------- | -------- | ------------------ |
| nas内绝对地址         | /m/1.mkv   | 源目录 `/s/m`   | /o/1.mkv   | /s/m/1.mkv (无效) | `/e/m`   | /e/m/1.mkv (无效)  |
| 刮削docker内绝对地址  | /s/m/1.mkv | 输出目录 `/s/o` | /s/o/1.mkv | /s/m/1.mkv        | ^        | /e/m/1.mkv (无效)  |
| emby-docker内绝对地址 | /e/m/1.mkv | ^               | /e/o/1.mkv | /s/m/1.mkv (无效) | ^        | /e/m/1.mkv         |

__注:__
1. 软链接只在有实际指向文件的环境内生效，适应范围单一
2. 软链接清理只需要删除源文件即可，硬链接需要删除源文件与硬连接后的文件


#### 致谢

[AV_Data_Capture](https://github.com/yoshiko2/AV_Data_Capture)
