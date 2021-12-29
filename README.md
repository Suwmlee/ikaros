
# ikaros

关联`transmission`/`qBittorrent`与`emby`，下载任务完成后，自动筛选文件创建软/硬链接，自动刮削JAV目录，推送emby库刷新。

- 批量软/硬链接
- 批量处理文件名，优化剧集命名
- JAV刮削
- 下载完成后脚本
- 自动化任务

### 安装

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

- 群晖docker
  待完善
  截图1

  截图2

__注意:__ 
- 默认Web访问端口:  __12346__
- 可以使用[watchtower](https://hub.docker.com/r/containrrr/watchtower)自动化更新Docker

### 文档

[使用说明](docs/intro.md)

### 感谢

[Movie_Data_Capture](https://github.com/yoshiko2/Movie_Data_Capture)
