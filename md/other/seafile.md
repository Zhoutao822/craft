

# 使用Docker方式安装Seafile私人网盘


参考：

> [用 Docker 部署 Seafile 服务](https://cloud.seafile.com/published/seafile-manual-cn/docker/%E7%94%A8Docker%E9%83%A8%E7%BD%B2Seafile.md)

Seafile 是一款开源的企业云盘，注重可靠性和性能。支持 Windows, Mac, Linux, iOS, Android 平台。支持文件同步或者直接挂载到本地访问。

<!-- more -->

## 1. Ubuntu服务器安装docker

参考[Docker方式安装chevereto图床]()

## 2. 配置docker-compose

首先在根目录下创建一个隐藏文件夹`.seafile`存放我们的配置文件以及挂载的数据卷，进入`.seafile`目录，并新建一个`docker-compose.yml`文件，`docker-compose.yml`内容如下，需要自行配置管理员账号和密码（**尽量不要修改80:80端口映射，我修改为其他端口号会导致拒绝访问**），`seafile-mysql、seafile-data`启动后会自动生成：

```yml
version: '2.0'
services:
  db:
    image: mariadb:10.1
    container_name: seafile-mysql
    environment:
      - MYSQL_ROOT_PASSWORD=root  # Requested, set the root's password of MySQL service.
      - MYSQL_LOG_CONSOLE=true
    # 挂载容器mysql数据到本地文件夹seafile-mysql
    volumes:
      - ./seafile-mysql:/var/lib/mysql  # Requested, specifies the path to MySQL data persistent store.
    networks:
      - seafile-net

  memcached:
    image: memcached:1.5.6
    container_name: seafile-memcached
    entrypoint: memcached -m 256
    networks:
      - seafile-net
          
  seafile:
    image: seafileltd/seafile-mc
    container_name: seafile
    ports:
      - "80:80"
      # - "443:443"  # If https is enabled, cancel the comment.
    # 挂载云盘数据到本地文件夹seafile-data
    volumes:
      - ./seafile-data:/shared   # Requested, specifies the path to Seafile data persistent store.
    environment:
      - DB_HOST=db
      - DB_ROOT_PASSWD=root  # Requested, the value shuold be root's password of MySQL service.
        #- TIME_ZONE=Asia/Shanghai # Optional, default is UTC. Should be uncomment and set to your local time zone.
      - SEAFILE_ADMIN_EMAIL=aaa@aaa.com # Specifies Seafile admin user, default is 'me@example.com'.
      - SEAFILE_ADMIN_PASSWORD=password     # Specifies Seafile admin password, default is 'asecret'.
      - SEAFILE_SERVER_LETSENCRYPT=false   # Whether use letsencrypt to generate cert.
      - SEAFILE_SERVER_HOSTNAME=175.24.47.141 # Specifies your host name.
    depends_on:
      - db
      - memcached
    networks:
      - seafile-net

networks:
  seafile-net:
```

不用修改权限，最后启动`docker-compose up -d`，然后就可以通过IP+端口号（如果配置了域名也可以用域名）访问seafile云盘了（**应该只能通过http访问，https是不可以的，除非配置过**）。首次登录如下：

{% asset_img seafile1.png %}

测试上传文件

{% asset_img seafile2.png %}

## 3. 数据迁移

同理，上面我们的`seafile-mysql`文件夹保存的是我们的账号信息等等，`seafile-data`保存了我们上传的文件数据、日志信息，如果我们需要从当前服务器迁移到另一个服务器只需要保存好`.seafile`中的所有内容，然后全部放到另一个服务器的`.seafile`目录中，不用设置权限，然后安装`docker`和`docker-compose`，然后执行`docker-compose up -d`就可以直接运行，我们的数据也会一起同步过来。

## 4. 启动seafile容器出错

如果启动seafile容器后无法访问，需要重新配置时，**务必先执行`docker-compose kill`和`docker-compose rm`停止并删除容器，再删除掉`seafile-mysql`和`seafile-data`两个文件夹**，之后再重新启动`docker-compose up -d`。


