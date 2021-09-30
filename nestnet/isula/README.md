# isula-py接口使用

### 说明

* isula-py主要进行容器的运行与管理。
* isula-py涉及到的对pod的操作一般为容器管理而服务，Pod的操作对用户不可见。

### 调用示例

```python
import isulapy.isula as isula

print(isula.version())
```

###  version

* 作用：获取当前系统安装的isula版本

* 参数：None
* 返回值：iSulad详细版本信息（class： VersionResponse）

### is_container_running

* 作用：判断当前容器是否正在运行
* 参数：container_id（str）
* 返回值：运行状态（bool类型）

### runcontainer

+ 作用：根据传入参数配置创建运行新的容器。

+ 参数：name：str，配置容器名称

  ​			config：dict，容器配置信息

+ 返回值：返回创建好的容器的详细信息（class：CreateContainerResponse）

### get_status 

* 作用：根据传入参数返回容器详细信息
* 参数：container_id（str）
* 返回值：容器信息（class：ListContainerResponse）

### update_resource

* 作用：根据传入参数更新容器资源

* 参数：name（Str：容器名称）

  ​            Resource（dict：容器资源配置）

* 返回值：是否成功更新资源（bool）

### pull_image 

* 作用：pull新镜像
* 参数：image_name（str：镜像名称）
* 返回值：是否成功拉取（bool）

### inspect_image

* 作用：获取镜像详细信息，包括cmd等
* 参数：image_name（str：镜像名称）
* 返回值：镜像详细信息（class：ImageStatusResponse）

### clean

* 作用：终止并删除所有正在运行的容器和Pod并回收资源
* 参数：None
* 返回值：None

