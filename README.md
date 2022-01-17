
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/suwmlee/ikaros/Release)](https://github.com/suwmlee/ikaros/actions) [![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/suwmlee/ikaros?color=blue&label=download&sort=semver)](https://github.com/suwmlee/ikaros/releases) [![Docker Pulls](https://img.shields.io/docker/pulls/suwmlee/ikaros)](https://hub.docker.com/r/suwmlee/ikaros)

# ikaros

关联`transmission`/`qBittorrent`与`emby`，下载完成后，自动筛选文件创建软/硬链接，刮削JAV目录，推送emby库刷新

- 批量软/硬链接
- 批量修改文件名，优化剧集名及自定义
- JAV刮削及自定义
- 自动托管

### 安装

本项目仅后端，需要搭配[ikaros-web](https://github.com/Suwmlee/ikaros-web)  
可自行编译或使用编译好的文件

- 使用编译好的[web release](https://github.com/Suwmlee/ikaros-web/tree/release)
  1. 将`index.html`放到`web/templates`
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
      --restart unless-stopped \
      suwmlee/ikaros:latest
    ```

- 群晖docker
  1. 设置卷
    ![path](docs/imgs/path.png)
  2. 设置端口
    ![port](docs/imgs/port.png)


__注:__ 
- 默认Web访问端口:  __12346__
- 可以使用[watchtower](https://hub.docker.com/r/containrrr/watchtower)自动化更新Docker

### 文档

[使用说明](docs/intro.md)

### 感谢

[Movie_Data_Capture](https://github.com/yoshiko2/Movie_Data_Capture)
