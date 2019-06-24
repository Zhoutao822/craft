# Google Play Bundles 使用流程

## 1. 简介

[Google App Bundles](https://developer.android.com/platform/technology/app-bundle)是一种基于Google Play的apk分发机制，它的主要作用是通过Google Play识别用户手机的各种参数例如屏幕分辨率、核心架构等等来加载相应的资源文件从而减少应用下载的大小，本质上我们并不需要对代码结构进行非常大的调整，最终我们编译得到是一个`.aab`文件而不是`.apk`，通过将`.aab`文件上传至Google Play，Google Play会自动完成分发工作。

## 2. 注意事项

完成 app signing 是使用App Bundles的**必要条件**，而且一旦Google Play上的Application加入了app signing，那是**不可退出的**。

### 2.1 App Signing 流程

1. 首先登录[Google Play Console](https://play.google.com/apps/publish/signup/)，这个需要developer账号；
2. 选择并进入需要接入Bundles的Application；

{% asset_img bundles-0.png %}
<!-- ![](bundles-0.png) -->

3. 根据下图显示，找到`Release management->App signing`，倘若此Application从未进行过App signing，则显示结果和下图相同；

{% asset_img bundles-1.png %}
<!-- ![](bundles-1.png) -->

4. 准备两种key：`app signing key`和`upload key`。`app signing key`是最终我们的应用发布出去被签名使用的key，`upload key`是用于上传apk或者aab文件到Google时使用的key。下面介绍一下以前使用签名发布应用的流程以及通过`upload key`发布应用的流程

```java
// 以前
用release keystore签名我们的应用 -> 上传至Google，Google验证签名是否相同 -> 如果签名相同则确认可以发布 -> 用户可以在Google Play上下载

// upload key + app signing key
用upload keystore签名我们的应用 -> 上传至Google，Google验证签名是否与保存在Google服务器的upload key相同 -> 如果签名相同则Google使用保存在Google服务器上的App signing key重新对应用签名，然后发布 -> 用户可以在Google Play上下载

这里的App signing key可以用我们以前的release keystore；新的upload key可以是重新创建的keystore（风险低），也可以与release keystore相同（风险高）。

使用upload key的好处：
1. 安全性，新创建的upload key仅用于上传应用时进行验证，如果丢失可以通过邮件重置upload key，不会对release key有威胁；
2. 便捷性，最终签名发布是由Google完成的。
```

5. 在上图的基础上选择`Export and upload a key from a Java keystore`

{% asset_img bundles-2.png %}
<!-- ![](bundles-2.png) -->

```java
1. 下载加密工具jar包PEPK；
2. 命令行使用pepk.jar加密我们的app signing key，可以在--output参数设置生成的文件类型为.pepk；
3. 上传.pepk文件；
4. upload key这里显示的是Optional，如果没有上传重新创建的upload key，那么默认upload key与app signing key相同，但是这样风险高；
5. 命令行导出upload key的证书，为.pem文件；
6. 上传.pem文件；
7. 如果上述格式都是正确的，那么我们提交之后的当前界面会变为下图。
```

{% asset_img bundles-3.png %}
<!-- ![](bundles-3.png) -->

6. 测试上传Bundles，使用upload key签名Bundles文件（注意版本号），在`Release management->App releases`上传`.aab`文件，如果步骤正确，则可以上传成功，然后填一下`Release name`和`What's new in this release?`，`SAVE`之后`REVIEW`，最后可以`Start rollout to production`

{% asset_img bundles-4.png %}
<!-- ![](bundles-4.png) -->

7. 如果rollout成功，那么就可以在Google Play上看到新发布的应用了。

{% asset_img bundles-5.png %}
<!-- ![](bundles-5.png) -->

### 2.2 可能存在的问题

[第三方登录功能失效](https://www.jianshu.com/p/86ffbf884f4a)（需要进一步测试）

[Building App Bundles Demo](https://codelabs.developers.google.com/codelabs/your-first-dynamic-app/index.html#0)
