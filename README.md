
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

|                       | 1.mkv      | 软链接配置 -->  | 软链接文件 | 实际指向地址      | 修正前缀 | 修正后实际指向地址 |
| --------------------- | ---------- | --------------- | ---------- | ----------------- | -------- | ------------------ |
| nas内绝对地址         | /m/1.mkv   | 源目录 `/s/m`   | /o/1.mkv   | /s/m/1.mkv (无效) | `/e/m`   | /e/m/1.mkv (无效)  |
| 刮削docker内绝对地址  | /s/m/1.mkv | 输出目录 `/s/o` | /s/o/1.mkv | /s/m/1.mkv        | ^        | /e/m/1.mkv (无效)  |
| emby-docker内绝对地址 | /e/m/1.mkv | ^               | /e/o/1.mkv | /s/m/1.mkv (无效) | ^        | /e/m/1.mkv         |

__注:__ 
1. 软链接只在存在实际指向文件的环境内生效，适应范围单一
2. 软链接清理只需要删除源文件即可，硬链接需要删除源文件与硬连接后的文件


#### 致谢

[AV_Data_Capture](https://github.com/yoshiko2/AV_Data_Capture)
