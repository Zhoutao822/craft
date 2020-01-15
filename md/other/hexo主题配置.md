RSS订阅

字体

为了解决 Google Fonts API 不稳定的问题，NexT 在 5.0.1 中引入此特性。 通过此特性，你可以指定所使用的字体库外链地址；与此同时，NexT 开放了 5 个特定范围的字体设定，他们是：

全局字体：定义的字体将在全站范围使用
标题字体：文章内标题的字体（h1, h2, h3, h4, h5, h6）
文章字体：文章所使用的字体
Logo字体：Logo 所使用的字体
代码字体： 代码块所使用的字体
各项所指定的字体将作为首选字体，当他们不可用时会自动 Fallback 到 NexT 设定的基础字体组：

非代码类字体：Fallback 到 "PingFang SC", "Microsoft YaHei", sans-serif
代码类字体： Fallback 到 consolas, Menlo, "PingFang SC", "Microsoft YaHei", monospace
另外，每一项都有一个额外的 external 属性，此属性用来控制是否使用外链字体库。 开放此属性方便你设定那些已经安装在系统中的字体，减少不必要的请求（请求大小）。



设置代码高亮主题
night


开启打赏功能

reward_comment: 坚持原创技术分享，您的支持将鼓励我继续创作！
wechatpay: /path/to/wechat-reward-image
alipay: /path/to/alipay-reward-image



设置「背景动画」



# canvas_nest
canvas_nest: true //开启动画
canvas_nest: false //关闭动画
# three_waves
three_waves: true //开启动画
three_waves: false //关闭动画


如需取消某个 页面/文章 的评论，在 md 文件的 front-matter 中增加 comments: false

DISQUS

不蒜子统计

文本居中的引用


<!-- 标签 方式，要求版本在0.4.5或以上 -->
{% centerquote %}blah blah blah{% endcenterquote %}



站内文章链接

{% post_link 文章标题 链接名称 %}



Text Align

text_align:
  # Available values: start | end | left | right | center | justify | justify-all | match-parent
  desktop: justify
  mobile: justify



Bookmark

bookmark:
  enable: false
  # Customize the color of the bookmark.
  color: "#222"
  # If auto, save the reading progress when closing the page or clicking the bookmark-icon.
  # If manual, only save it by clicking the bookmark-icon.
  save: auto


  https://tding.top/archives/42c38b10


  Hexo 文章永久链接插件
Hexo 站点地图 sitemap 生成
Hexo 文章置顶插件

Hexo 页面静态资源压缩插件


