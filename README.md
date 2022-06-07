
# ikaros

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/suwmlee/ikaros/Release)](https://github.com/suwmlee/ikaros/actions) [![GitHub release (latest)](https://img.shields.io/github/v/release/suwmlee/ikaros.svg)](https://github.com/suwmlee/ikaros/releases) [![Docker Pulls](https://img.shields.io/docker/pulls/suwmlee/ikaros)](https://hub.docker.com/r/suwmlee/ikaros)

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
      -e PUID=0 \
      -e PGID=0 \
      -p 12346:12346 \
      -v /path/to/media:/media \
      -v /path/to/data:/ikaros/database \
      --restart unless-stopped \
      suwmlee/ikaros:latest
    ```
  默认 `PUID=1000 PGID=1000`,此处PUID,PGID为0，即使用root用户权限，也可以用 __id__ 命令查找具体用户值:
  ```
  $ id username
    uid=1000(ikaros) gid=1000(ikarosgroup) groups=1000(ikarosgroup)
  ```

- 群晖docker
  1. 设置卷
    <img src="docs/imgs/path.png" alt="set-vol" width="600"/>

  2. 设置端口
    <img src="docs/imgs/port.png" alt="set-port" width="600"/>


__注:__ 
- 默认Web访问端口:  __12346__
- 可以使用[watchtower](https://hub.docker.com/r/containrrr/watchtower)自动化更新Docker

### 默认WEB界面预览

 
|                 刮削                  |                    转移文件                     |
| :-----------------------------------: | :---------------------------------------------: |
|   ![javview](docs/imgs/javview.png)   |   ![transferview](docs/imgs/transferview.png)   |
| ![javmodify](docs/imgs/javmodify.png) | ![transfermodify](docs/imgs/transfermodify.png) |

### 文档

[使用说明](docs/intro.md)

### 感谢

[Movie_Data_Capture](https://github.com/yoshiko2/Movie_Data_Capture)
