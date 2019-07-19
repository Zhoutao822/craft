---
category:
- Android
tags:
- Android
- Http
- Https
- Retrofit
- OkHttp
- 工厂模式
---

参考：

> [HTTPS Tutorials](https://www.tutorialsteacher.com/https)
> [HTTP 协议入门](http://www.ruanyifeng.com/blog/2016/08/http.html)
> [Retrofit](https://square.github.io/retrofit/)
> [OkHttp](https://square.github.io/okhttp/)
> [OkHttp使用详解](https://juejin.im/post/5a31db566fb9a045257820b2#heading-2)
> [Introduction to Retrofit](https://www.baeldung.com/retrofit)
> [Android Retrofit 2.5.0使用基础详解](https://juejin.im/post/5c9cb008e51d455ec63f7aa6)
> [Retrofit使用拦截器添加Cookie](https://juejin.im/post/5d1f2462f265da1bbc6ff5e8#heading-13)
> [Factory Pattern](https://design-patterns.readthedocs.io/zh_CN/latest/creational_patterns/simple_factory.html)

Http，超文本传输协议，Https，更加安全的超文本传输协议，目前大量用于客户端与服务端之间的信息交流，属于应用层协议，下面有传输层TCP协议、网络层IP协议以及数据链路层为其提供保障。以登录功能为例，每一次输入账户密码后点击登录按钮就做了一次对服务器的Http请求（POST），我们收到的结果比如账号密码错误或者登录成功等信息就是服务器对Http请求的回复。Http与Https的区别在于后者采用了SSL（Secure Socket Layer安全套接层），简而言之就是对传输的数据进行了加密。具体细节可以在[HTTPS Tutorials](https://www.tutorialsteacher.com/https)或者其他资料中找到。

<!-- more -->

## 1. GET和POST

Http协议中比较常用的请求是GET和POST请求，可以说大部分客户端与服务端之间的数据交互都是通过这两个请求方法，以GET和POST请求为例

GET用于请求数据，按照设计要求，GET请求不会对服务器数据进行修改，也就是说我们通过GET可以请求各种资源（静态页面等等），其中比较重要的参数包括：

Host：需要请求的服务器

User-Agent：代理，表明你的身份，一般来说浏览器发送的请求会自动添加，可以人为修改伪造身份

Connection：可以建立TCP长连接，属于HTTP/1.1的优化功能

这个GET请求的目的就是从www.wrox.com这个服务器取index.htm这个页面

```http
GET /index.htm HTTP/1.1
Host: www.wrox.com
User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.6)
Gecko/20050225 Firefox/1.0.1
Connection: Keep-Alive
```

POST请求用于修改服务器数据，按照设计的要求，可以通过POST方法可以向服务器提交数据由服务器处理后返回，这里比较重要的参数包括：

Content-Type：请求实体的格式

Content-Length：请求实体的长度

以及请求实体的内容，会空一行再写，比如这里的name1=value1&name2=value2

这个POST请求的目的是向w3schools.com服务器下/test/demo_form.asp发送数据参数name1=value1&name2=value2，然后服务器会返回处理后的结果

```http
POST /test/demo_form.asp HTTP/1.1
Host: w3schools.com
User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.6)
Gecko/20050225 Firefox/1.0.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 40
Connection: Keep-Alive

name1=value1&name2=value2
```

以上就是Http中GET和POST方法的简要介绍了，实际上Http协议还包括一些其他方法，以及TCP握手、SSL握手等建立连接的过程、对称与非对称加密等细节步骤，这里就不多描述，可以看其他资料。

## 2. OkHttp

OkHttp是一个封装好的Http请求客户端，它既可用于Java项目也可以用于Android项目，通过调用构建好的http client，我们就可以发出http请求。

**Android中需要网络权限**`<uses-permission android:name="android.permission.INTERNET" />`

### 2.1 OkHttp.GET

> 1.创建OkHttpClient对象

```java
OkHttpClient client = new OkHttpClient();
```

> 2.创建Request对象，URL则为我们需要的请求URL，一般来说此URL包含了Host、请求内容，比如`https://zhoutao822.coding.me/2019/01/03/XGBoost/0.png`

```java
Request request = new Request.Builder()
        .url(URL)
        .build();
```

> 3.将Request封装为Call

```java
Call call = client.newCall(request);
```

> 4.调用同步或异步的请求方法

```java
// 这是异步调用，通过enqueue方法
call.enqueue(new Callback() {
    @Override
    public void onFailure(Call call, IOException e) {
        Toast.makeText(MainActivity.this, "get failed", Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onResponse(Call call, Response response) throws IOException {
        final String ret = response.body().string();
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                textView.setText(ret);
            }
        });
    }
});
```

```java
// 这是同步调用
Response response = call.execute();
```

异步调用意味着可以在主线程中调用call.enqueue方法，而同步调用方式只能在另一个线程中调用，通过handler将数据传回主线程，完整代码为

```java
public class MainActivity extends AppCompatActivity {

    private final static String URL = "https://free-api.heweather.net/s6/weather/now?location=beijing&key=XXXXXXXXX";

    private static Handler handler = new Handler();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        final TextView textView = findViewById(R.id.text);

        OkHttpClient client = new OkHttpClient();
        Request request = new Request.Builder()
                .get()
                .url(URL)
                .build();
        Call call = client.newCall(request);
        call.enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Toast.makeText(MainActivity.this, "get failed", Toast.LENGTH_SHORT).show();
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                final String ret = response.body().string();
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        textView.setText(ret);
                    }
                });
            }
        });

// 下面是同步调用
//        new Thread(new Runnable() {
//            @Override
//            public void run() {
//                OkHttpClient client = new OkHttpClient();
//                Request request = new Request.Builder()
//                        .get()
//                        .url(URL)
//                        .build();
//                Call call = client.newCall(request);
//                try {
//                    final Response response = call.execute();
//                    handler.post(new Runnable() {
//                        @Override
//                        public void run() {
//                            try {
//                                textView.setText(response.body().string());
//                            } catch (IOException e) {
//                                e.printStackTrace();
//                            }
//                        }
//                    });
//                } catch (IOException e) {
//                    e.printStackTrace();
//                }
//
//            }
//        }).start();

    }
}
```

GET请求下载文件，对于图片url，我们也可以通过GET的方式进行下载，将返回的数据转为本地图片或者直接用在ImageView上

```java
    public void downloadImg(View view) {
        OkHttpClient client = new OkHttpClient();
        Request request = new Request.Builder()
                .get()
                .url(URL)
                .build();
        Call call = client.newCall(request);
        call.enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e("aaaa", "onFailure: ");
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                //拿到字节流
                InputStream is = response.body().byteStream();

                int len = 0;
                File file = new File(Environment.getExternalStorageDirectory(), "image.png");
                FileOutputStream fos = new FileOutputStream(file);
                byte[] buf = new byte[128];

                while ((len = is.read(buf)) != -1) {
                    fos.write(buf, 0, len);
                }

                fos.flush();
                //关闭流
                fos.close();
                is.close();

// 下面是直接把图片放到ImageView上                
//                final Bitmap bitmap = BitmapFactory.decodeStream(is);
//                runOnUiThread(new Runnable() {
//                    @Override
//                    public void run() {
//                        imageView.setImageBitmap(bitmap);
//                    }
//                });
//
//                is.close();
            }
        });
    }
```

GET请求下载文件的同时我们可以计算出下载进度，通过`response.body().contentLength()`拿到文件总大小，只需要修改上面的`onResponse`方法

```java
            @Override
            public void onResponse(Call call, Response response) throws IOException {
                //拿到字节流
                InputStream is = response.body().byteStream();

                int len = 0;
                long sum = 0L;
                final long total = response.body().contentLength();

                File file = new File(Environment.getExternalStorageDirectory(), "image.png");
                FileOutputStream fos = new FileOutputStream(file);
                byte[] buf = new byte[128];

                while ((len = is.read(buf)) != -1) {
                    fos.write(buf, 0, len);
                    sum += len;
                    final long finalSum = sum;
                    Log.i("aaaa", "onResponse: " + finalSum + "/" + total);
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            //将进度设置到TextView中
                            textView.setText(finalSum + "/" + total);
                        }
                    });
                }

                fos.flush();
                //关闭流
                fos.close();
                is.close();
            }
```

### 2.2 OkHttp.POST

POST与GET非常类似，以传入键值对数据为例

> 1.创建OkHttpClient对象

```java
OkHttpClient client = new OkHttpClient();
```

> 2.构建FormBody，传入参数

```java
FormBody formBody = new FormBody.Builder()
                .add("username", "admin")
                .add("password", "admin")
                .build();
```

> 3.创建Request对象，URL则为我们需要的请求URL，一般将此URL作为BaseUrl，比如`https://www.wanandroid.com/user/login`，我们就知道通过这个URL可以发送登录请求，根据API文档直到传入的参数包括`username`和`password`，因此需要FormBody

```java
Request request = new Request.Builder()
        .url(URL)
        .post(formBody)
        .build();
```

> 4.将Request封装为Call

```java
Call call = client.newCall(request);
```

> 5.调用异步的请求方法

```java
call.enqueue(new Callback() {
    @Override
    public void onFailure(Call call, IOException e) {
        Log.e("aaaa", "onFailure: ");
    }

    @Override
    public void onResponse(Call call, Response response) throws IOException {
        final String res = response.body().string();
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                textView.setText(res);
            }
        });
    }
});
```

POST除了可以发送键值对FormBody形式的请求外，还可以发送json字符串，将FormBody替换为RequestBody

```java
RequestBody requestBody = RequestBody.create(MediaType.parse("text/plain;charset=utf-8"), "{username:admin;password:admin}");
```

除了以上两种形式的数据之外，Http还可以接受表单形式的数据请求，这也是正常情况下登录流程中发送账号密码的要求，通过表单保存这些数据，再发送到服务器上

```java
File file = new File(Environment.getExternalStorageDirectory(), "image.png");
if (!file.exists()){
    Toast.makeText(this, "文件不存在", Toast.LENGTH_SHORT).show();
    return;
}
RequestBody muiltipartBody = new MultipartBody.Builder()
        //一定要设置这句
        .setType(MultipartBody.FORM)
        .addFormDataPart("username", "admin")
        .addFormDataPart("password", "admin")
        .addFormDataPart("myfile", "image.png", RequestBody.create(MediaType.parse("application/octet-stream"), file))
        .build();
```

在发送表单请求时，除了字符串还可以添加二进制文件，比如这里将图片转为二进制加入到了表单中。

除了在表单中上传文件之外，还可以直接发送二进制文件，需要存储权限`<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>`

```java
File file = new File(Environment.getExternalStorageDirectory(), "image.png");
if (!file.exists()){
    Toast.makeText(this, "文件不存在", Toast.LENGTH_SHORT).show();
}else{
    RequestBody requestBody2 = RequestBody.create(MediaType.parse("application/octet-stream"), file);
}
```

POST也可以显示上传进度，但是需要自定义接口

```java
public class CountingRequestBody extends RequestBody {
    //实际起作用的RequestBody
    private RequestBody delegate;
    //回调监听
    private Listener listener;

    private CountingSink countingSink;

    /**
     * 构造函数初始化成员变量
     * @param delegate
     * @param listener
     */
    public CountingRequestBody(RequestBody delegate, Listener listener){
        this.delegate = delegate;
        this.listener = listener;
    }
    @Override
    public MediaType contentType() {
        return delegate.contentType();
    }

    @Override
    public void writeTo(BufferedSink sink) throws IOException {
        countingSink = new CountingSink(sink);
        //将CountingSink转化为BufferedSink供writeTo()使用
        BufferedSink bufferedSink = Okio.buffer(countingSink);
        delegate.writeTo(bufferedSink);
        bufferedSink.flush();
    }

    protected final class CountingSink extends ForwardingSink{
        private long byteWritten;
        public CountingSink(Sink delegate) {
            super(delegate);
        }

        /**
         * 上传时调用该方法,在其中调用回调函数将上传进度暴露出去,该方法提供了缓冲区的自己大小
         * @param source
         * @param byteCount
         * @throws IOException
         */
        @Override
        public void write(Buffer source, long byteCount) throws IOException {
            super.write(source, byteCount);
            byteWritten += byteCount;
            listener.onRequestProgress(byteWritten, contentLength());
        }
    }

    /**
     * 返回文件总的字节大小
     * 如果文件大小获取失败则返回-1
     * @return
     */
    @Override
    public long contentLength(){
        try {
            return delegate.contentLength();
        } catch (IOException e) {
            return -1;
        }
    }

    /**
     * 回调监听接口
     */
    public static interface Listener{
        /**
         * 暴露出上传进度
         * @param byteWritted  已经上传的字节大小
         * @param contentLength 文件的总字节大小
         */
        void onRequestProgress(long byteWritted, long contentLength);
    }
}
```

```java
File file = new File(Environment.getExternalStorageDirectory(), "image.png");
if (!file.exists()){
    Toast.makeText(this, "文件不存在", Toast.LENGTH_SHORT).show();
}else{
    RequestBody requestBody2 = RequestBody.create(MediaType.parse("application/octet-stream"), file);
}

//使用我们自己封装的类
CountingRequestBody countingRequestBody = new CountingRequestBody(requestBody2, new CountingRequestBody.Listener() {
    @Override
    public void onRequestProgress(long byteWritted, long contentLength) {
        //打印进度
        Log.d("aaaa", "进度 ：" + byteWritted + "/" + contentLength);
    }
});
```

### 2.3 OkHttp源码分析

以发送表单数据请求为例，大致有4步：OkHttpClient构建 -> RequestBody构建 -> Request构建 -> Call构建并调用

首先看一下OkHttpClient到底是个什么东西，从注释中可以知道OkHttpClient时Call的工厂，具体发送HTTP请求以及接收服务器响应都是通过Call来实现的。

OkHttpClient还包括以下几个特性：

1. OkHttpClient应该用单例模式，这样是为了复用减少内存消耗；
2. 每一个OkHttpClient都持有独立的连接池和线程池；
3. 直接new出来的OkHttpClient是默认配置的；
4. `new OkHttpClient.Builder()`可以对Client进行配置；
5. 通过`client.newBuilder()`可以得到一个与client共享连接池和线程池的OkHttpClient，仅在特殊情形下需要；
6. OkHttpClient不是必须主动关闭，client持有的线程和连接在空闲的情况下会被自动回收；
7. 如果需要主动回收，`client.dispatcher().executorService().shutdown()`可以回收执行的Service，但会导致之后的call被拒绝；
8. `client.connectionPool().evictAll()`会回收连接池；
9. `client.cache().close()`会回收Client的缓存（如果在第4步中配置了的话）。

调用默认构造方法话，则默认参数为

```java
public Builder() {
    dispatcher = new Dispatcher(); // Dispatcher持有ExecutorService，通过ExecutorService调用call
    protocols = DEFAULT_PROTOCOLS; // 默认支持HTTP/2和HTTP/1.1
    connectionSpecs = DEFAULT_CONNECTION_SPECS; // 默认连接配置，支持TLS加密的https和普通的不加密http
    eventListenerFactory = EventListener.factory(EventListener.NONE); // 提供监听各种Event的Listener，通常需要继承EventListener并实现其方法
    proxySelector = ProxySelector.getDefault(); // 设置代理，默认是获取系统范围的代理
    if (proxySelector == null) {
    proxySelector = new NullProxySelector(); // 如果系统没有设置代理则将proxySelector设置为NullProxySelector
    }
    cookieJar = CookieJar.NO_COOKIES; // CookieJar是一个接口，实现这个接口的方法可以保存Cookies，也可以在发送请求时加上Cookies
    socketFactory = SocketFactory.getDefault(); // SocketFactory用于构建socket，默认返回DefaultSocketFactory，通过DefaultSocketFactory可以创建Socket
    hostnameVerifier = OkHostnameVerifier.INSTANCE; // 用于在握手期间验证URL主机名和server的身份信息是否相同
    certificatePinner = CertificatePinner.DEFAULT; // CertificatePinner用于在发送请求的过程中嵌入证书（Certificate Pinning），可以防止连接到危险的服务器
    proxyAuthenticator = Authenticator.NONE; // 代理服务器需要身份验证的时候需要用到，默认不需要身份验证
    authenticator = Authenticator.NONE; 
    connectionPool = new ConnectionPool(); // 默认连接池允许最大5个空闲连接，超过5分钟空闲会被回收
    dns = Dns.SYSTEM; // DNS服务，默认使用系统的DNS服务
    followSslRedirects = true; // 重定向到https域名，下面都是一些简单配置参数
    followRedirects = true;
    retryOnConnectionFailure = true;
    callTimeout = 0;
    connectTimeout = 10_000;
    readTimeout = 10_000;
    writeTimeout = 10_000;
    pingInterval = 0;
}
```

client只在后面构建Call的时候用到，那先看一下RequestBody，RequestBody是个抽象类

```java
// 如果需要自定义RequestBody，则需要继承RequestBody并实现两个抽象方法contentType和writeTo，
// 一般来说contentType返回此RequestBody的Content-Type，contentLength返回Content的大小，
// 重写writeTo方法实际上是调用BufferedSink的write(content)方法
// RequestBody包含几个默认的create，如果只是发送简单请求，Content的内容不太复杂可以直接使用
public abstract class RequestBody {
  /** Returns the Content-Type header for this body. */
  public abstract @Nullable MediaType contentType();

  /**
   * Returns the number of bytes that will be written to {@code sink} in a call to {@link #writeTo},
   * or -1 if that count is unknown.
   */
  public long contentLength() throws IOException {
    return -1;
  }

  /** Writes the content of this request to {@code sink}. */
  public abstract void writeTo(BufferedSink sink) throws IOException;

  /**
   * Returns a new request body that transmits {@code content}. If {@code contentType} is non-null
   * and lacks a charset, this will use UTF-8.
   */
  public static RequestBody create(@Nullable MediaType contentType, String content) {
    Charset charset = Util.UTF_8;
    if (contentType != null) {
      charset = contentType.charset();
      if (charset == null) {
        charset = Util.UTF_8;
        contentType = MediaType.parse(contentType + "; charset=utf-8");
      }
    }
    byte[] bytes = content.getBytes(charset);
    return create(contentType, bytes);
  }

  /** Returns a new request body that transmits {@code content}. */
  public static RequestBody create(
      final @Nullable MediaType contentType, final ByteString content) {
    return new RequestBody() {
      @Override public @Nullable MediaType contentType() {
        return contentType;
      }

      @Override public long contentLength() throws IOException {
        return content.size();
      }

      @Override public void writeTo(BufferedSink sink) throws IOException {
        sink.write(content);
      }
    };
  }

  /** Returns a new request body that transmits {@code content}. */
  public static RequestBody create(final @Nullable MediaType contentType, final byte[] content) {
    return create(contentType, content, 0, content.length);
  }

  /** Returns a new request body that transmits {@code content}. */
  public static RequestBody create(final @Nullable MediaType contentType, final byte[] content,
      final int offset, final int byteCount) {
    if (content == null) throw new NullPointerException("content == null");
    Util.checkOffsetAndCount(content.length, offset, byteCount);
    return new RequestBody() {
      @Override public @Nullable MediaType contentType() {
        return contentType;
      }

      @Override public long contentLength() {
        return byteCount;
      }

      @Override public void writeTo(BufferedSink sink) throws IOException {
        sink.write(content, offset, byteCount);
      }
    };
  }

  /** Returns a new request body that transmits the content of {@code file}. */
  public static RequestBody create(final @Nullable MediaType contentType, final File file) {
    if (file == null) throw new NullPointerException("file == null");

    return new RequestBody() {
      @Override public @Nullable MediaType contentType() {
        return contentType;
      }

      @Override public long contentLength() {
        return file.length();
      }

      @Override public void writeTo(BufferedSink sink) throws IOException {
        Source source = null;
        try {
          source = Okio.source(file);
          sink.writeAll(source);
        } finally {
          Util.closeQuietly(source);
        }
      }
    };
  }
}
```

MultipartBody继承自RequestBody，通过MultipartBody构建RequestBody可以发送更加复杂的数据，比如`multipart/form-data`表单数据，通过MultipartBody的内部类Builder可以对MultipartBody进行配置（建造者模式）

```java
// Builder有几个重要的方法
// setType：设置MultipartBody请求的Content-Type，如果是表单数据则为MultipartBody.FORM；
// addPart：因为HTTP请求包括Header和Body，因此通过内部类Part封装号Header和Body，
// 将Part保存到RequestBody的List<Part>中，可能是为了一次发送多个请求；
// addFormDataPart：通过Part构造表单请求；
// build：最后通过build方法创建MultipartBody实例，参数来源于前面三个方法
  public static final class Builder {
    private final ByteString boundary;
    private MediaType type = MIXED;
    private final List<Part> parts = new ArrayList<>();

    public Builder() {
      // 初始化一个随机的boundary，暂时还不知道有什么用
      this(UUID.randomUUID().toString());
    }

    public Builder(String boundary) {
      this.boundary = ByteString.encodeUtf8(boundary);
    }

    /**
     * Set the MIME type. Expected values for {@code type} are {@link #MIXED} (the default), {@link
     * #ALTERNATIVE}, {@link #DIGEST}, {@link #PARALLEL} and {@link #FORM}.
     */
    public Builder setType(MediaType type) {
      if (type == null) {
        throw new NullPointerException("type == null");
      }
      if (!type.type().equals("multipart")) {
        throw new IllegalArgumentException("multipart != " + type);
      }
      this.type = type;
      return this;
    }

    /** Add a part to the body. */
    public Builder addPart(RequestBody body) {
      return addPart(Part.create(body));
    }

    /** Add a part to the body. */
    public Builder addPart(@Nullable Headers headers, RequestBody body) {
      return addPart(Part.create(headers, body));
    }

    /** Add a form data part to the body. */
    public Builder addFormDataPart(String name, String value) {
      return addPart(Part.createFormData(name, value));
    }

    /** Add a form data part to the body. */
    public Builder addFormDataPart(String name, @Nullable String filename, RequestBody body) {
      return addPart(Part.createFormData(name, filename, body));
    }

    /** Add a part to the body. */
    public Builder addPart(Part part) {
      if (part == null) throw new NullPointerException("part == null");
      parts.add(part);
      return this;
    }

    /** Assemble the specified parts into a request body. */
    public MultipartBody build() {
      if (parts.isEmpty()) {
        throw new IllegalStateException("Multipart body must have at least one part.");
      }
      return new MultipartBody(boundary, type, parts);
    }
  }
```

```java
// Part用于构造包含Header和RequestBody的实例，简单来说就是用Header封装好要发送请求的首部参数，
// 用RequestBody封装要发送请求的请求数据
  public static final class Part {
    public static Part create(RequestBody body) {
      return create(null, body);
    }

    public static Part create(@Nullable Headers headers, RequestBody body) {
      if (body == null) {
        throw new NullPointerException("body == null");
      }
      if (headers != null && headers.get("Content-Type") != null) {
        throw new IllegalArgumentException("Unexpected header: Content-Type");
      }
      if (headers != null && headers.get("Content-Length") != null) {
        throw new IllegalArgumentException("Unexpected header: Content-Length");
      }
      return new Part(headers, body);
    }

    public static Part createFormData(String name, String value) {
      return createFormData(name, null, RequestBody.create(null, value));
    }

    public static Part createFormData(String name, @Nullable String filename, RequestBody body) {
      if (name == null) {
        throw new NullPointerException("name == null");
      }
      StringBuilder disposition = new StringBuilder("form-data; name=");
      appendQuotedString(disposition, name);

      if (filename != null) {
        disposition.append("; filename=");
        appendQuotedString(disposition, filename);
      }

      return create(Headers.of("Content-Disposition", disposition.toString()), body);
    }

    final @Nullable Headers headers;
    final RequestBody body;

    private Part(@Nullable Headers headers, RequestBody body) {
      this.headers = headers;
      this.body = body;
    }

    public @Nullable Headers headers() {
      return headers;
    }

    public RequestBody body() {
      return body;
    }
  }
```

RequestBody包含了请求首部参数以及请求数据，接下来需要分析Request，Request连接了请求的主机url和RequestBody

```java
// Request默认构造的是GET请求
    public Builder() {
      this.method = "GET";
      this.headers = new Headers.Builder();
    }

// 通过url方法设置请求的主机名，如果直接传入的是HttpUrl也可以，传入String也可以，
// 但是会进行格式验证，会把ws:开头和wss:开头的主机名转换为http:和https:
    public Builder url(HttpUrl url) {
      if (url == null) throw new NullPointerException("url == null");
      this.url = url;
      return this;
    }

    /**
     * Sets the URL target of this request.
     *
     * @throws IllegalArgumentException if {@code url} is not a valid HTTP or HTTPS URL. Avoid this
     * exception by calling {@link HttpUrl#parse}; it returns null for invalid URLs.
     */
    public Builder url(String url) {
      if (url == null) throw new NullPointerException("url == null");

      // Silently replace web socket URLs with HTTP URLs.
      if (url.regionMatches(true, 0, "ws:", 0, 3)) {
        url = "http:" + url.substring(3);
      } else if (url.regionMatches(true, 0, "wss:", 0, 4)) {
        url = "https:" + url.substring(4);
      }

      return url(HttpUrl.get(url));
    }

// post以及其他方法都是通过传入字符POST或者其他方式调用method
    public Builder get() {
      return method("GET", null);
    }

    public Builder head() {
      return method("HEAD", null);
    }

    public Builder post(RequestBody body) {
      return method("POST", body);
    }

    public Builder delete(@Nullable RequestBody body) {
      return method("DELETE", body);
    }

    public Builder delete() {
      return delete(Util.EMPTY_REQUEST);
    }

    public Builder put(RequestBody body) {
      return method("PUT", body);
    }

    public Builder patch(RequestBody body) {
      return method("PATCH", body);
    }

// method方法还是将Request的属性设为method传入的值
    public Builder method(String method, @Nullable RequestBody body) {
      if (method == null) throw new NullPointerException("method == null");
      if (method.length() == 0) throw new IllegalArgumentException("method.length() == 0");
      if (body != null && !HttpMethod.permitsRequestBody(method)) {
        throw new IllegalArgumentException("method " + method + " must not have a request body.");
      }
      if (body == null && HttpMethod.requiresRequestBody(method)) {
        throw new IllegalArgumentException("method " + method + " must have a request body.");
      }
      this.method = method;
      this.body = body;
      return this;
    }    

// build()方法返回Request对象，并且传入了上面设置的属性
    public Request build() {
      if (url == null) throw new IllegalStateException("url == null");
      return new Request(this);
    }

// 其实Request对象也没有什么具体的功能，也是类似RequestBody封装了HTTP请求的一些参数，包括url请求主机名，method请求的方法，
// headers这里也有headers，也就是说我们可以在RequestBody中加入请求首部参数，也可以在Request中加入请求参数，而且Request会覆盖
// RequestBody的参数，在两个地方都封装Header，我觉得应该是为了复用，有些时候Header对于一些请求来说都是相同的，区别只是Body不同
// 因此在Request中设置Header能减少冗余的代码
  Request(Builder builder) {
    this.url = builder.url;
    this.method = builder.method;
    this.headers = builder.headers.build();
    this.body = builder.body;
    this.tags = Util.immutableMap(builder.tags);
  }
```

以上的RequestBody和Request实际上并没有任何复杂的功能，都是对一个完整的HTTP请求参数的封装，利用了建造者模式，同时将请求数据与请求首部参数以及请求方法和主机名进行解耦，使得开发人员可以灵活的使用各个模块组建一个完整的Request，如何发送这个Request，并接收回调则是在Call中进行的

```java
// OkHttpClient.java 之前说过OkHttpClient是Call的工厂类，通过newCall方法传入上面构造的Request实例，
// 得到一个Call实例，具体的实现是通过RealCall.newRealCall方法
  @Override public Call newCall(Request request) {
    return RealCall.newRealCall(this, request, false /* for web socket */);
  }
```

在看RealCall.newRealCall之前首先看一下Call

```java
// 根据注释说明，我们直到Call是一个接口，Call接口的实现类能够完成具体的HTTP请求发送，且包含request/response对，
// 也就意味着可以通过Call的回调获取到服务器返回的数据，一个call不能被执行两次
/**
 * A call is a request that has been prepared for execution. A call can be canceled. As this object
 * represents a single request/response pair (stream), it cannot be executed twice.
 */
public interface Call extends Cloneable {
  /** Returns the original request that initiated this call. */
  Request request();
// execute方法执行时会阻塞当前线程，直到处理完response
  Response execute() throws IOException;
// enqueue方法会通过dispatcher安排request进入队列等待执行，执行完毕后通过Callback回调
  void enqueue(Callback responseCallback);
// 调用cancel方法可以取消request
  void cancel();
// 判断call是否已经在执行，比如调用了execute或者enqueue方法
  boolean isExecuted();
// 判断call是否被取消
  boolean isCanceled();
// 返回整个call执行期间的耗时，包括DNS寻址、连接、写入request body、服务器处理、读取response body等过程
  Timeout timeout();
// 复制此call，利用clone得到的call可以继续执行
  Call clone();

  interface Factory {
    Call newCall(Request request);
  }
}
```

RealCall实现了Call的接口，所以上面用到的方法都是在RealCall中实现的，首先看RealCall.newRealCall

```java
  private RealCall(OkHttpClient client, Request originalRequest, boolean forWebSocket) {
    this.client = client;
    this.originalRequest = originalRequest;
    this.forWebSocket = forWebSocket;
    this.retryAndFollowUpInterceptor = new RetryAndFollowUpInterceptor(client, forWebSocket);
    this.timeout = new AsyncTimeout() {
      @Override protected void timedOut() {
        cancel();
      }
    };
    this.timeout.timeout(client.callTimeoutMillis(), MILLISECONDS);
  }
// newRealCall方法也是仅仅只做了参数传递的工作，最主要的参数是client和originalRequest
  static RealCall newRealCall(OkHttpClient client, Request originalRequest, boolean forWebSocket) {
    // Safely publish the Call instance to the EventListener.
    RealCall call = new RealCall(client, originalRequest, forWebSocket);
    call.eventListener = client.eventListenerFactory().create(call);
    return call;
  }
```

> 当我们调用call.execute方法时

```java
  @Override public Response execute() throws IOException {
    // synchronized锁，确保同一个Call不会被执行两次
    synchronized (this) {
      if (executed) throw new IllegalStateException("Already Executed");
      executed = true;
    }
    // captureCallStackTrace跟踪call执行的堆栈
    captureCallStackTrace();
    // timeout.enter开始记录timeout
    timeout.enter();
    // 将Call Start事件传递出去，通过自定义eventListenerFactory可以对事件进行处理
    eventListener.callStart(this);
    try {
      //  通过dispatcher调用executed执行请求发送，实际上只是把call加到一个队列中，并没有执行发送请求
      client.dispatcher().executed(this);
      // 通过getResponseWithInterceptorChain获取服务器返回的response，这里才是真正的call被发送出去
      Response result = getResponseWithInterceptorChain();
      if (result == null) throw new IOException("Canceled");
      return result;
    } catch (IOException e) {
      e = timeoutExit(e);
      eventListener.callFailed(this, e);
      throw e;
    } finally {
      client.dispatcher().finished(this);
    }
  }
```

```java
// Dispatcher.java client.dispatcher().executed(this);
  /** Used by {@code Call#execute} to signal it is in-flight. */
  synchronized void executed(RealCall call) {
    runningSyncCalls.add(call);
  }
```

```java
// Interceptor也是一个接口，实现Interceptor接口的类可以对Request进行拦截，也就是通过
// 各种Interceptor来实现HTTP请求，比如这里的BridgeInterceptor、CacheInterceptor、
// ConnectInterceptor等等
  Response getResponseWithInterceptorChain() throws IOException {
    // Build a full stack of interceptors.
    // 注意默认构造的client.interceptors()为空
    List<Interceptor> interceptors = new ArrayList<>();
    interceptors.addAll(client.interceptors());
    interceptors.add(retryAndFollowUpInterceptor);
    interceptors.add(new BridgeInterceptor(client.cookieJar()));
    interceptors.add(new CacheInterceptor(client.internalCache()));
    interceptors.add(new ConnectInterceptor(client));
    if (!forWebSocket) {
      interceptors.addAll(client.networkInterceptors());
    }
    interceptors.add(new CallServerInterceptor(forWebSocket));
// 这里调用的时候，注意index为0，而RealInterceptorChain调用proceed方法
    Interceptor.Chain chain = new RealInterceptorChain(interceptors, null, null, null, 0,
        originalRequest, this, eventListener, client.connectTimeoutMillis(),
        client.readTimeoutMillis(), client.writeTimeoutMillis());

    return chain.proceed(originalRequest);
  }
```

```java
// RealInterceptorChain.java chain.proceed(originalRequest)的位置，这里的index为0
  public Response proceed(Request request, StreamAllocation streamAllocation, HttpCodec httpCodec,
      RealConnection connection) throws IOException {
    if (index >= interceptors.size()) throw new AssertionError();

    calls++;

    // If we already have a stream, confirm that the incoming request will use it.
    if (this.httpCodec != null && !this.connection.supportsUrl(request.url())) {
      throw new IllegalStateException("network interceptor " + interceptors.get(index - 1)
          + " must retain the same host and port");
    }

    // If we already have a stream, confirm that this is the only call to chain.proceed().
    if (this.httpCodec != null && calls > 1) {
      throw new IllegalStateException("network interceptor " + interceptors.get(index - 1)
          + " must call proceed() exactly once");
    }
// 注意这里，创建了next RealInterceptorChain，index为1，而interceptors.get(index)拿的就是上文对应的retryAndFollowUpInterceptor
    // Call the next interceptor in the chain.
    RealInterceptorChain next = new RealInterceptorChain(interceptors, streamAllocation, httpCodec,
        connection, index + 1, request, call, eventListener, connectTimeout, readTimeout,
        writeTimeout);
    Interceptor interceptor = interceptors.get(index);
    // 即response时通过BridgeInterceptor的intercept方法得到的
    Response response = interceptor.intercept(next);

    // Confirm that the next interceptor made its required call to chain.proceed().
    if (httpCodec != null && index + 1 < interceptors.size() && next.calls != 1) {
      throw new IllegalStateException("network interceptor " + interceptor
          + " must call proceed() exactly once");
    }

    // Confirm that the intercepted response isn't null.
    if (response == null) {
      throw new NullPointerException("interceptor " + interceptor + " returned null");
    }

    if (response.body() == null) {
      throw new IllegalStateException(
          "interceptor " + interceptor + " returned a response with no body");
    }

    return response;
  }
```

```java
// RetryAndFollowUpInterceptor.java RetryAndFollowUpInterceptor用于请求重连，通过connectionPool
// 构建StreamAllocation，StreamAllocation用于管理连接、数据流以及Calls
  @Override public Response intercept(Chain chain) throws IOException {
    Request request = chain.request();
    RealInterceptorChain realChain = (RealInterceptorChain) chain;
    Call call = realChain.call();
    EventListener eventListener = realChain.eventListener();

    StreamAllocation streamAllocation = new StreamAllocation(client.connectionPool(),
        createAddress(request.url()), call, eventListener, callStackTrace);
    this.streamAllocation = streamAllocation;

    int followUpCount = 0;
    Response priorResponse = null;
    // 通过while死循环发送request
    while (true) {
      if (canceled) {
        streamAllocation.release();
        throw new IOException("Canceled");
      }

      Response response;
      boolean releaseConnection = true;
      try {
        // 这里的realChain交接给BridgeInterceptor
        response = realChain.proceed(request, streamAllocation, null, null);
        releaseConnection = false;
      } catch (RouteException e) {
        // The attempt to connect via a route failed. The request will not have been sent.
        if (!recover(e.getLastConnectException(), streamAllocation, false, request)) {
          throw e.getFirstConnectException();
        }
        releaseConnection = false;
        continue;
      } catch (IOException e) {
        // An attempt to communicate with a server failed. The request may have been sent.
        boolean requestSendStarted = !(e instanceof ConnectionShutdownException);
        if (!recover(e, streamAllocation, requestSendStarted, request)) throw e;
        releaseConnection = false;
        continue;
      } finally {
        // We're throwing an unchecked exception. Release any resources.
        if (releaseConnection) {
          streamAllocation.streamFailed(null);
          streamAllocation.release();
        }
      }

      // Attach the prior response if it exists. Such responses never have a body.
      if (priorResponse != null) {
        response = response.newBuilder()
            .priorResponse(priorResponse.newBuilder()
                    .body(null)
                    .build())
            .build();
      }
      // 仅仅在发送请求后接收到response，并且没有后续的request时返回，返回值为response
      Request followUp;
      try {
        followUp = followUpRequest(response, streamAllocation.route());
      } catch (IOException e) {
        streamAllocation.release();
        throw e;
      }

      if (followUp == null) {
        streamAllocation.release();
        return response;
      }

      closeQuietly(response.body());

      if (++followUpCount > MAX_FOLLOW_UPS) {
        streamAllocation.release();
        throw new ProtocolException("Too many follow-up requests: " + followUpCount);
      }

      if (followUp.body() instanceof UnrepeatableRequestBody) {
        streamAllocation.release();
        throw new HttpRetryException("Cannot retry streamed HTTP body", response.code());
      }

      if (!sameConnection(response, followUp.url())) {
        streamAllocation.release();
        streamAllocation = new StreamAllocation(client.connectionPool(),
            createAddress(followUp.url()), call, eventListener, callStackTrace);
        this.streamAllocation = streamAllocation;
      } else if (streamAllocation.codec() != null) {
        throw new IllegalStateException("Closing the body of " + response
            + " didn't close its backing stream. Bad interceptor?");
      }

      request = followUp;
      priorResponse = response;
    }
  }
```


```java
// BridgeInterceptor.java
  @Override public Response intercept(Chain chain) throws IOException {
    // 通过chain得到request
    Request userRequest = chain.request();
    Request.Builder requestBuilder = userRequest.newBuilder();
    // 拿到body
    RequestBody body = userRequest.body();
    if (body != null) {
      MediaType contentType = body.contentType();
      if (contentType != null) {
        // 重新构造header
        requestBuilder.header("Content-Type", contentType.toString());
      }

      long contentLength = body.contentLength();
      if (contentLength != -1) {
        requestBuilder.header("Content-Length", Long.toString(contentLength));
        requestBuilder.removeHeader("Transfer-Encoding");
      } else {
        requestBuilder.header("Transfer-Encoding", "chunked");
        requestBuilder.removeHeader("Content-Length");
      }
    }

    if (userRequest.header("Host") == null) {
      requestBuilder.header("Host", hostHeader(userRequest.url(), false));
    }

    if (userRequest.header("Connection") == null) {
      requestBuilder.header("Connection", "Keep-Alive");
    }

    // If we add an "Accept-Encoding: gzip" header field we're responsible for also decompressing
    // the transfer stream.
    boolean transparentGzip = false;
    if (userRequest.header("Accept-Encoding") == null && userRequest.header("Range") == null) {
      transparentGzip = true;
      requestBuilder.header("Accept-Encoding", "gzip");
    }
    // 构造带Cookies的header，默认Cookies为空
    List<Cookie> cookies = cookieJar.loadForRequest(userRequest.url());
    if (!cookies.isEmpty()) {
      requestBuilder.header("Cookie", cookieHeader(cookies));
    }

    if (userRequest.header("User-Agent") == null) {
      requestBuilder.header("User-Agent", Version.userAgent());
    }
    // 注意这里的chain的index为1，所以再次调用chain.proceed会使index为2，即CacheInterceptor
    Response networkResponse = chain.proceed(requestBuilder.build());

    HttpHeaders.receiveHeaders(cookieJar, userRequest.url(), networkResponse.headers());

    Response.Builder responseBuilder = networkResponse.newBuilder()
        .request(userRequest);

    if (transparentGzip
        && "gzip".equalsIgnoreCase(networkResponse.header("Content-Encoding"))
        && HttpHeaders.hasBody(networkResponse)) {
      GzipSource responseBody = new GzipSource(networkResponse.body().source());
      Headers strippedHeaders = networkResponse.headers().newBuilder()
          .removeAll("Content-Encoding")
          .removeAll("Content-Length")
          .build();
      responseBuilder.headers(strippedHeaders);
      String contentType = networkResponse.header("Content-Type");
      responseBuilder.body(new RealResponseBody(contentType, -1L, Okio.buffer(responseBody)));
    }

    return responseBuilder.build();
  }
```

```java
// CacheInterceptor.java CacheInterceptor用于从cache中取request以及向cache中写入response
// 如果cache中保存了相同request的response，那么可以实现断网也可以获取response
  @Override public Response intercept(Chain chain) throws IOException {
    Response cacheCandidate = cache != null
        ? cache.get(chain.request())
        : null;

    long now = System.currentTimeMillis();

    CacheStrategy strategy = new CacheStrategy.Factory(now, chain.request(), cacheCandidate).get();
    Request networkRequest = strategy.networkRequest;
    Response cacheResponse = strategy.cacheResponse;

    if (cache != null) {
      cache.trackResponse(strategy);
    }

    if (cacheCandidate != null && cacheResponse == null) {
      closeQuietly(cacheCandidate.body()); // The cache candidate wasn't applicable. Close it.
    }

    // If we're forbidden from using the network and the cache is insufficient, fail.
    if (networkRequest == null && cacheResponse == null) {
      return new Response.Builder()
          .request(chain.request())
          .protocol(Protocol.HTTP_1_1)
          .code(504)
          .message("Unsatisfiable Request (only-if-cached)")
          .body(Util.EMPTY_RESPONSE)
          .sentRequestAtMillis(-1L)
          .receivedResponseAtMillis(System.currentTimeMillis())
          .build();
    }
// 没有网络则从cache中取对应的response
    // If we don't need the network, we're done.
    if (networkRequest == null) {
      return cacheResponse.newBuilder()
          .cacheResponse(stripBody(cacheResponse))
          .build();
    }

    Response networkResponse = null;
    try {
      // 注意这里同理chain交接给下一个ConnectInterceptor
      networkResponse = chain.proceed(networkRequest);
    } finally {
      // If we're crashing on I/O or otherwise, don't leak the cache body.
      if (networkResponse == null && cacheCandidate != null) {
        closeQuietly(cacheCandidate.body());
      }
    }

    // If we have a cache response too, then we're doing a conditional get.
    if (cacheResponse != null) {
      if (networkResponse.code() == HTTP_NOT_MODIFIED) {
        Response response = cacheResponse.newBuilder()
            .headers(combine(cacheResponse.headers(), networkResponse.headers()))
            .sentRequestAtMillis(networkResponse.sentRequestAtMillis())
            .receivedResponseAtMillis(networkResponse.receivedResponseAtMillis())
            .cacheResponse(stripBody(cacheResponse))
            .networkResponse(stripBody(networkResponse))
            .build();
        networkResponse.body().close();

        // Update the cache after combining headers but before stripping the
        // Content-Encoding header (as performed by initContentStream()).
        cache.trackConditionalCacheHit();
        cache.update(cacheResponse, response);
        return response;
      } else {
        closeQuietly(cacheResponse.body());
      }
    }

    Response response = networkResponse.newBuilder()
        .cacheResponse(stripBody(cacheResponse))
        .networkResponse(stripBody(networkResponse))
        .build();

    if (cache != null) {
      if (HttpHeaders.hasBody(response) && CacheStrategy.isCacheable(response, networkRequest)) {
        // Offer this request to the cache.
        CacheRequest cacheRequest = cache.put(response);
        return cacheWritingResponse(cacheRequest, response);
      }

      if (HttpMethod.invalidatesCache(networkRequest.method())) {
        try {
          cache.remove(networkRequest);
        } catch (IOException ignored) {
          // The cache cannot be written.
        }
      }
    }

    return response;
  }

```

```java
// ConnectInterceptor.java StreamAllocation在RetryAndFollowUpInterceptor中被构造用于管理连接
// 因此ConnectInterceptor用于创建真实的HTTP连接RealConnection
  @Override public Response intercept(Chain chain) throws IOException {
    RealInterceptorChain realChain = (RealInterceptorChain) chain;
    Request request = realChain.request();
    StreamAllocation streamAllocation = realChain.streamAllocation();

    // We need the network to satisfy this request. Possibly for validating a conditional GET.
    boolean doExtensiveHealthChecks = !request.method().equals("GET");
    HttpCodec httpCodec = streamAllocation.newStream(client, chain, doExtensiveHealthChecks);
    RealConnection connection = streamAllocation.connection();
// 同理下一任是CallServerInterceptor，因为networkInterceptors为空
    return realChain.proceed(request, streamAllocation, httpCodec, connection);
  }
```

```java
// CallServerInterceptor.java CallServerInterceptor是最后一任Interceptor，它的功能是发送网络Call到服务器
  @Override public Response intercept(Chain chain) throws IOException {
    RealInterceptorChain realChain = (RealInterceptorChain) chain;
    HttpCodec httpCodec = realChain.httpStream();
    StreamAllocation streamAllocation = realChain.streamAllocation();
    RealConnection connection = (RealConnection) realChain.connection();
    Request request = realChain.request();

    long sentRequestMillis = System.currentTimeMillis();
// 将HeadersStart和HeadersEnd通过eventListener传出去
    realChain.eventListener().requestHeadersStart(realChain.call());
    // 发送请求的方式是通过httpCodec数据流，首先传出去request
    httpCodec.writeRequestHeaders(request);
    realChain.eventListener().requestHeadersEnd(realChain.call(), request);

// 然后通过httpCodec读取response，其中涉及到request的首部是否包含Expect: 100-continue，不过问题不大
    Response.Builder responseBuilder = null;
    if (HttpMethod.permitsRequestBody(request.method()) && request.body() != null) {
      // If there's a "Expect: 100-continue" header on the request, wait for a "HTTP/1.1 100
      // Continue" response before transmitting the request body. If we don't get that, return
      // what we did get (such as a 4xx response) without ever transmitting the request body.
      if ("100-continue".equalsIgnoreCase(request.header("Expect"))) {
        // 如果request的首部包含Expect: 100-continue参数，responseBuilder会被置为null
        httpCodec.flushRequest();
        realChain.eventListener().responseHeadersStart(realChain.call());
        responseBuilder = httpCodec.readResponseHeaders(true);
      }

      if (responseBuilder == null) {
        // Write the request body if the "Expect: 100-continue" expectation was met.
        realChain.eventListener().requestBodyStart(realChain.call());
        long contentLength = request.body().contentLength();
        // 通过httpCodec创建request数据流，可以通过CountingSink监控数据传输
        CountingSink requestBodyOut =
            new CountingSink(httpCodec.createRequestBody(request, contentLength));
        BufferedSink bufferedRequestBody = Okio.buffer(requestBodyOut);

        request.body().writeTo(bufferedRequestBody);
        bufferedRequestBody.close();
        realChain.eventListener()
            .requestBodyEnd(realChain.call(), requestBodyOut.successfulCount);
      } else if (!connection.isMultiplexed()) {
        // If the "Expect: 100-continue" expectation wasn't met, prevent the HTTP/1 connection
        // from being reused. Otherwise we're still obligated to transmit the request body to
        // leave the connection in a consistent state.
        streamAllocation.noNewStreams();
      }
    }

    httpCodec.finishRequest();

    if (responseBuilder == null) {
      realChain.eventListener().responseHeadersStart(realChain.call());
      // 通过httpCodec的readResponseHeaders读取response的header信息，此时responseBuilder不为空
      responseBuilder = httpCodec.readResponseHeaders(false);
    }
// 通过responseBuilder构建完整的response
    Response response = responseBuilder
        .request(request)
        .handshake(streamAllocation.connection().handshake())
        .sentRequestAtMillis(sentRequestMillis)
        .receivedResponseAtMillis(System.currentTimeMillis())
        .build();

    int code = response.code();
    if (code == 100) {
      // server sent a 100-continue even though we did not request one.
      // try again to read the actual response
      responseBuilder = httpCodec.readResponseHeaders(false);

      response = responseBuilder
              .request(request)
              .handshake(streamAllocation.connection().handshake())
              .sentRequestAtMillis(sentRequestMillis)
              .receivedResponseAtMillis(System.currentTimeMillis())
              .build();

      code = response.code();
    }

    realChain.eventListener()
            .responseHeadersEnd(realChain.call(), response);

    if (forWebSocket && code == 101) {
      // Connection is upgrading, but we need to ensure interceptors see a non-null response body.
      response = response.newBuilder()
          .body(Util.EMPTY_RESPONSE)
          .build();
    } else {
      // 通过httpCodec的openResponseBody创建读取response的body的数据流
      response = response.newBuilder()
          .body(httpCodec.openResponseBody(response))
          .build();
    }

    if ("close".equalsIgnoreCase(response.request().header("Connection"))
        || "close".equalsIgnoreCase(response.header("Connection"))) {
      streamAllocation.noNewStreams();
    }

    if ((code == 204 || code == 205) && response.body().contentLength() > 0) {
      throw new ProtocolException(
          "HTTP " + code + " had non-zero Content-Length: " + response.body().contentLength());
    }
// 最后返回构建好的response
    return response;
  }
```

以上就是通过call.execute返回response的流程，这里可以发现并没有使用到Service或者多线程，因此在等待服务器响应的过程中会阻塞当前线程，因此Android中不宜直接使用execute方法。

> 当我们调用call.enqueue方法时

```java
  @Override public void enqueue(Callback responseCallback) {
    synchronized (this) {
      if (executed) throw new IllegalStateException("Already Executed");
      executed = true;
    }
    captureCallStackTrace();
    eventListener.callStart(this);
    // 通过dispatcher将responseCallback入队
    client.dispatcher().enqueue(new AsyncCall(responseCallback));
  }
```

```java
// Dispatcher.java
  void enqueue(AsyncCall call) {
    synchronized (this) {
      readyAsyncCalls.add(call);
    }
    // 调用promoteAndExecute执行发送请求
    promoteAndExecute();
  }

  /**
   * Promotes eligible calls from {@link #readyAsyncCalls} to {@link #runningAsyncCalls} and runs
   * them on the executor service. Must not be called with synchronization because executing calls
   * can call into user code.
   *
   * @return true if the dispatcher is currently running calls.
   */
  private boolean promoteAndExecute() {
    assert (!Thread.holdsLock(this));

    List<AsyncCall> executableCalls = new ArrayList<>();
    boolean isRunning;
    synchronized (this) {
      // 将readyAsyncCalls中的Call加入到executableCalls中
      for (Iterator<AsyncCall> i = readyAsyncCalls.iterator(); i.hasNext(); ) {
        AsyncCall asyncCall = i.next();

        if (runningAsyncCalls.size() >= maxRequests) break; // Max capacity.
        if (runningCallsForHost(asyncCall) >= maxRequestsPerHost) continue; // Host max capacity.

        i.remove();
        executableCalls.add(asyncCall);
        runningAsyncCalls.add(asyncCall);
      }
      isRunning = runningCallsCount() > 0;
    }

    for (int i = 0, size = executableCalls.size(); i < size; i++) {
      AsyncCall asyncCall = executableCalls.get(i);
      // 通过遍历executableCalls，调用每一个Call的executeOn方法，其中使用到了初始化过程中引入的线程池executorService
      asyncCall.executeOn(executorService());
    }

    return isRunning;
  }

  public synchronized ExecutorService executorService() {
    if (executorService == null) {
      executorService = new ThreadPoolExecutor(0, Integer.MAX_VALUE, 60, TimeUnit.SECONDS,
          new SynchronousQueue<Runnable>(), Util.threadFactory("OkHttp Dispatcher", false));
    }
    return executorService;
  }

    /**
     * Attempt to enqueue this async call on {@code executorService}. This will attempt to clean up
     * if the executor has been shut down by reporting the call as failed.
     */
    void executeOn(ExecutorService executorService) {
      assert (!Thread.holdsLock(client.dispatcher()));
      boolean success = false;
      try {
        // 关键代码通过线程池executorService执行此Call，又因为AsyncCall继承自NamedRunnable，因此，调用
        // AsyncCall的run方法时，执行的是NamedRunnable的run
        executorService.execute(this);
        success = true;
      } catch (RejectedExecutionException e) {
        InterruptedIOException ioException = new InterruptedIOException("executor rejected");
        ioException.initCause(e);
        eventListener.callFailed(RealCall.this, ioException);
        responseCallback.onFailure(RealCall.this, ioException);
      } finally {
        if (!success) {
          client.dispatcher().finished(this); // This call is no longer running!
        }
      }
    }  
```

```java
/**
 * Runnable implementation which always sets its thread name.
 */
public abstract class NamedRunnable implements Runnable {
  protected final String name;

  public NamedRunnable(String format, Object... args) {
    this.name = Util.format(format, args);
  }

  @Override public final void run() {
    String oldName = Thread.currentThread().getName();
    Thread.currentThread().setName(name);
    try {
      // 这里的execute由AsyncCall实现
      execute();
    } finally {
      Thread.currentThread().setName(oldName);
    }
  }

  protected abstract void execute();
}
```

```java
    @Override protected void execute() {
      boolean signalledCallback = false;
      timeout.enter();
      try {
        // 最终又回到了getResponseWithInterceptorChain方法，后面的不用多说
        Response response = getResponseWithInterceptorChain();
        if (retryAndFollowUpInterceptor.isCanceled()) {
          signalledCallback = true;
          // 与此同时我们通过responseCallback.onFailure将事件回调出去
          responseCallback.onFailure(RealCall.this, new IOException("Canceled"));
        } else {
          signalledCallback = true;
          // 同上
          responseCallback.onResponse(RealCall.this, response);
        }
      } catch (IOException e) {
        e = timeoutExit(e);
        if (signalledCallback) {
          // Do not signal the callback twice!
          Platform.get().log(INFO, "Callback failure for " + toLoggableString(), e);
        } else {
          eventListener.callFailed(RealCall.this, e);
          responseCallback.onFailure(RealCall.this, e);
        }
      } finally {
        client.dispatcher().finished(this);
      }
    }
  }
```

综上，OkHttp的源码中采用了非常多的有意思的设计模式，比如建造者模式，对于HTTP请求来说，我们需要一些公用的资源比如线程池、连接池等，将这些公共资源设置在OkHttpClient中，然后通过单例模式引用，节省了很多资源消耗；

对于RequestBody以及Request这种参数设置非常多的实体，通过建造者模式保存其参数；

在构建请求实体Call的时候采用了OkHttpClient工厂类，同时发送request的过程中利用了链式传递的方式，既增加了开发人员自定义的Interceptor，又可以利用原本定义好的Interceptor。

## 3. Retrofit

Retrofit也是一个网络请求框架，且Retrofit是基于OkHttp的，实际网络请求的功能由OkHttp来实现，但是Retrofit实现了额外的功能，比如利用Gson进行数据实体化、兼容RxJava等等，是一个比较流行的网络请求工具。

### 3.1 Retrofit使用

需要`implementation 'com.squareup.retrofit2:retrofit:2.6.0'`

以请求和风天气数据为例，通过GET请求，加上location参数和key参数，服务器返回json数据，我们将json数据实体化，首先看一下返回的json格式

```json
{
    "HeWeather6": [
        {
            "basic": {
                "cid": "CN101010100",
                "location": "北京",
                "parent_city": "北京",
                "admin_area": "北京",
                "cnty": "中国",
                "lat": "39.90498734",
                "lon": "116.4052887",
                "tz": "+8.00"
            },
            "update": {
                "loc": "2019-07-18 16:45",
                "utc": "2019-07-18 08:45"
            },
            "status": "ok",
            "now": {
                "cloud": "10",
                "cond_code": "101",
                "cond_txt": "多云",
                "fl": "35",
                "hum": "54",
                "pcpn": "0.0",
                "pres": "1000",
                "tmp": "32",
                "vis": "6",
                "wind_deg": "279",
                "wind_dir": "西风",
                "wind_sc": "1",
                "wind_spd": "3"
            }
        }
    ]
}
```

> 1.根据json数据构建我们的实体类WeatherEntity，这里使用的Android Studio的插件GsonFormat，可以直接根据json数据生成代码

```java
public class WeatherEntity {

    private List<HeWeather6Bean> HeWeather6;

    public List<HeWeather6Bean> getHeWeather6() {
        return HeWeather6;
    }

    public void setHeWeather6(List<HeWeather6Bean> HeWeather6) {
        this.HeWeather6 = HeWeather6;
    }
// 重写以下toString方法，便于后续观察数据传输是否正确
    @NonNull
    @Override
    public String toString() {
        return HeWeather6.get(0).toString();
    }

    public static class HeWeather6Bean {
        /**
         * basic : {"cid":"CN101010100","location":"北京","parent_city":"北京","admin_area":"北京","cnty":"中国","lat":"39.90498734","lon":"116.4052887","tz":"+8.00"}
         * update : {"loc":"2019-07-18 16:45","utc":"2019-07-18 08:45"}
         * status : ok
         * now : {"cloud":"10","cond_code":"101","cond_txt":"多云","fl":"35","hum":"54","pcpn":"0.0","pres":"1000","tmp":"32","vis":"6","wind_deg":"279","wind_dir":"西风","wind_sc":"1","wind_spd":"3"}
         */

        private BasicBean basic;
        private UpdateBean update;
        private String status;
        private NowBean now;

        @NonNull
        @Override
        public String toString() {
            return status + " \n " + basic.toString() + " \n " + update.toString() + " \n " + now.toString();
        }

        public BasicBean getBasic() {
            return basic;
        }

        public void setBasic(BasicBean basic) {
            this.basic = basic;
        }

        public UpdateBean getUpdate() {
            return update;
        }

        public void setUpdate(UpdateBean update) {
            this.update = update;
        }

        public String getStatus() {
            return status;
        }

        public void setStatus(String status) {
            this.status = status;
        }

        public NowBean getNow() {
            return now;
        }

        public void setNow(NowBean now) {
            this.now = now;
        }

        public static class BasicBean {
            /**
             * cid : CN101010100
             * location : 北京
             * parent_city : 北京
             * admin_area : 北京
             * cnty : 中国
             * lat : 39.90498734
             * lon : 116.4052887
             * tz : +8.00
             */

            private String cid;
            private String location;
            private String parent_city;
            private String admin_area;
            private String cnty;
            private String lat;
            private String lon;
            private String tz;

            @NonNull
            @Override
            public String toString() {
                return "cid : " + cid + "\n" +
                        "location : " + location + "\n" +
                        "parent_city : " + parent_city + "\n" +
                        "admin_area : " + admin_area + "\n" +
                        "cnty : " + cnty + "\n" +
                        "lat : " + lat + "\n" +
                        "lon : " + lon + "\n" +
                        "tz : " + tz + "\n";
            }

            public String getCid() {
                return cid;
            }

            public void setCid(String cid) {
                this.cid = cid;
            }

            public String getLocation() {
                return location;
            }

            public void setLocation(String location) {
                this.location = location;
            }

            public String getParent_city() {
                return parent_city;
            }

            public void setParent_city(String parent_city) {
                this.parent_city = parent_city;
            }

            public String getAdmin_area() {
                return admin_area;
            }

            public void setAdmin_area(String admin_area) {
                this.admin_area = admin_area;
            }

            public String getCnty() {
                return cnty;
            }

            public void setCnty(String cnty) {
                this.cnty = cnty;
            }

            public String getLat() {
                return lat;
            }

            public void setLat(String lat) {
                this.lat = lat;
            }

            public String getLon() {
                return lon;
            }

            public void setLon(String lon) {
                this.lon = lon;
            }

            public String getTz() {
                return tz;
            }

            public void setTz(String tz) {
                this.tz = tz;
            }
        }

        public static class UpdateBean {
            /**
             * loc : 2019-07-18 16:45
             * utc : 2019-07-18 08:45
             */

            private String loc;
            private String utc;

            @NonNull
            @Override
            public String toString() {
                return "loc : " + loc + "\n" +
                        "utc : " + utc + "\n";
            }

            public String getLoc() {
                return loc;
            }

            public void setLoc(String loc) {
                this.loc = loc;
            }

            public String getUtc() {
                return utc;
            }

            public void setUtc(String utc) {
                this.utc = utc;
            }
        }

        public static class NowBean {
            /**
             * cloud : 10
             * cond_code : 101
             * cond_txt : 多云
             * fl : 35
             * hum : 54
             * pcpn : 0.0
             * pres : 1000
             * tmp : 32
             * vis : 6
             * wind_deg : 279
             * wind_dir : 西风
             * wind_sc : 1
             * wind_spd : 3
             */

            private String cloud;
            private String cond_code;
            private String cond_txt;
            private String fl;
            private String hum;
            private String pcpn;
            private String pres;
            private String tmp;
            private String vis;
            private String wind_deg;
            private String wind_dir;
            private String wind_sc;
            private String wind_spd;

            @NonNull
            @Override
            public String toString() {
                return "cloud : " + cloud + "\n" +
                        "cond_code : " + cond_code + "\n" +
                        "cond_txt : " + cond_txt + "\n" +
                        "fl : " + fl + "\n" +
                        "hum : " + hum + "\n" +
                        "pcpn : " + pcpn + "\n" +
                        "pres : " + pres + "\n" +
                        "tmp : " + tmp + "\n" +
                        "vis : " + vis + "\n" +
                        "wind_deg : " + wind_deg + "\n" +
                        "wind_dir : " + wind_dir + "\n" +
                        "wind_sc : " + wind_sc + "\n" +
                        "wind_spd : " + wind_spd + "\n";
            }

            public String getCloud() {
                return cloud;
            }

            public void setCloud(String cloud) {
                this.cloud = cloud;
            }

            public String getCond_code() {
                return cond_code;
            }

            public void setCond_code(String cond_code) {
                this.cond_code = cond_code;
            }

            public String getCond_txt() {
                return cond_txt;
            }

            public void setCond_txt(String cond_txt) {
                this.cond_txt = cond_txt;
            }

            public String getFl() {
                return fl;
            }

            public void setFl(String fl) {
                this.fl = fl;
            }

            public String getHum() {
                return hum;
            }

            public void setHum(String hum) {
                this.hum = hum;
            }

            public String getPcpn() {
                return pcpn;
            }

            public void setPcpn(String pcpn) {
                this.pcpn = pcpn;
            }

            public String getPres() {
                return pres;
            }

            public void setPres(String pres) {
                this.pres = pres;
            }

            public String getTmp() {
                return tmp;
            }

            public void setTmp(String tmp) {
                this.tmp = tmp;
            }

            public String getVis() {
                return vis;
            }

            public void setVis(String vis) {
                this.vis = vis;
            }

            public String getWind_deg() {
                return wind_deg;
            }

            public void setWind_deg(String wind_deg) {
                this.wind_deg = wind_deg;
            }

            public String getWind_dir() {
                return wind_dir;
            }

            public void setWind_dir(String wind_dir) {
                this.wind_dir = wind_dir;
            }

            public String getWind_sc() {
                return wind_sc;
            }

            public void setWind_sc(String wind_sc) {
                this.wind_sc = wind_sc;
            }

            public String getWind_spd() {
                return wind_spd;
            }

            public void setWind_spd(String wind_spd) {
                this.wind_spd = wind_spd;
            }
        }
    }
}
```

> 2.构建请求Api，请求url格式为`https://free-api.heweather.net/s6/weather/now?location=beijing&key=xxx`，因此将`https://free-api.heweather.net/s6/weather/`作为baseUrl（baseUrl必须以`/`结尾），`now?`作为请求url主体，后面的两个作为参数通过`@Query`加入

```java
public interface Api {
    // 通过@Query("location")的方式可以自动将location=location连接到我们的请求url后面
    @GET("now?")
    Call<WeatherEntity> getNowWeather(@Query("location") String location, @Query("key") String key);
    // 如果需要使用RxJava，需要修改返回类型为Observable
    // @GET("now?")
    // Observable<WeatherEntity> getNowWeather(@Query("location") String location, @Query("key") String key);
}
```

> 3.构建Retrofit实体，需要`implementation 'com.squareup.retrofit2:converter-gson:2.6.0'`，这里的版本号和Retrofit相同即可，如果需要RxJava2，则添加`implementation 'com.squareup.retrofit2:adapter-rxjava2:2.6.0'`

```java
Retrofit retrofit = new Retrofit.Builder()
        .baseUrl(URL) // 设置网络请求的公共Url地址
        .addConverterFactory(GsonConverterFactory.create()) // 设置数据解析器Gson
//      .addCallAdapterFactory(RxJava2CallAdapterFactory.create())   // 如果需要使用RxJava2     
        .build();     

```

> 4.构造接口实体

```java
Api api = retrofit.create(Api.class);
```

> 5.构造Call，这里的Call是retrofit2的Call，与okHttp的Call还是不一样的，如果是使用RxJava2，则为Observable

```java
retrofit2.Call<WeatherEntity> call = api.getNowWeather("beijing", KEY);
// Observable<WeatherEntity> observable = api.getNowWeather("beijing", KEY);
```

> 6.调用call.enqueue发送请求

```java
call.enqueue(new retrofit2.Callback<WeatherEntity>() {
    @Override
    public void onResponse(retrofit2.Call<WeatherEntity> call, retrofit2.Response<WeatherEntity> response) {
        WeatherEntity entity = response.body();
        textView.setText(entity.toString());
    }

    @Override
    public void onFailure(retrofit2.Call<WeatherEntity> call, Throwable t) {

    }
});
// 如果是RxJava则按照设计在io线程请求数据，在mainThread主线程显示结果
// observable.subscribeOn(Schedulers.io())
//         .observeOn(AndroidSchedulers.mainThread())
//         .subscribe(new Consumer<WeatherEntity>() {
//             @Override
//             public void accept(WeatherEntity weatherEntity) throws Exception {

//             }
//         }, new Consumer<Throwable>() {
//             @Override
//             public void accept(Throwable throwable) throws Exception {
                
//             }
//         });
```

### 3.2 Retrofit源码分析

Retrofit也采用了建造者模式，通过`new Retrofit.Builder()`初始化Retrofit对象

```java
// Retrofit.java 这里初始化Retrofit对象的时候需要参数Platform，看来是和平台相关
// 我们直到OkHttp是Java和Android相同都可以使用的，但是OkHttp没有做平台判断，
// Retrofit需要平台判断应该是与后面一些功能相关
    public Builder() {
      this(Platform.get());
    }

// --------------------------------------------------------------------------

// Platform.java
  private static final Platform PLATFORM = findPlatform();

  static Platform get() {
    return PLATFORM;
  }
// 通过findPlatform获取平台信息
  private static Platform findPlatform() {
    try {
      // 判断的方式简单粗暴，直接通过Class.forName找系统的类，通过抛出异常终止，妙啊妙啊
      Class.forName("android.os.Build");
      if (Build.VERSION.SDK_INT != 0) {
        // 这里只看Android类
        return new Android();
      }
    } catch (ClassNotFoundException ignored) {
    }
    try {
      // 同理对Java平台
      Class.forName("java.util.Optional");
      return new Java8();
    } catch (ClassNotFoundException ignored) {
    }
    return new Platform();
  }

// Android继承自Platform
  static class Android extends Platform {
    @IgnoreJRERequirement // Guarded by API check.
    @Override boolean isDefaultMethod(Method method) {
      if (Build.VERSION.SDK_INT < 24) {
        return false;
      }
      return method.isDefault();
    }
    // defaultCallbackExecutor返回了MainThreadExecutor，Executor是一个接口，
    // 实现此接口的类需要完成execute方法，通过execute方法可以运行Runnable对象
    @Override public Executor defaultCallbackExecutor() {
      return new MainThreadExecutor();
    }
    // 两个关键的类CallAdapter和Converter，CallAdapter用于转换Call的类型，以RxJava2CallAdapterFactory为例，
    // 如果在构造Retrofit对象时加上了addCallAdapterFactory(RxJava2CallAdapterFactory.create())，
    // 则需要对Api类中的方法返回值类型进行修改，改为RxJava支持的Observable类型，然后就可以通过RxJava的方式发送请求；
    // Converter用于对Response的Body进行格式转换，以GsonConverterFactory为例，可以将Response的Body中的json数据实体化，
    // 直接转换为我们定义的对象。
    @Override List<? extends CallAdapter.Factory> defaultCallAdapterFactories(
        @Nullable Executor callbackExecutor) {
      if (callbackExecutor == null) throw new AssertionError();
      // 根据BuildSDKVersion决定用DefaultCallAdapterFactory还是CompletableFutureCallAdapterFactory
      // 暂时用不到，稍后再分析
      DefaultCallAdapterFactory executorFactory = new DefaultCallAdapterFactory(callbackExecutor);
      return Build.VERSION.SDK_INT >= 24
        ? asList(CompletableFutureCallAdapterFactory.INSTANCE, executorFactory)
        : singletonList(executorFactory);
    }

    @Override int defaultCallAdapterFactoriesSize() {
      return Build.VERSION.SDK_INT >= 24 ? 2 : 1;
    }

    @Override List<? extends Converter.Factory> defaultConverterFactories() {
      // 同CallAdapter
      return Build.VERSION.SDK_INT >= 24
          ? singletonList(OptionalConverterFactory.INSTANCE)
          : Collections.<Converter.Factory>emptyList();
    }

    @Override int defaultConverterFactoriesSize() {
      return Build.VERSION.SDK_INT >= 24 ? 1 : 0;
    }
    // MainThreadExecutor实现了Executor接口，通过主线程的Handler运行Runnable对象
    static class MainThreadExecutor implements Executor {
      private final Handler handler = new Handler(Looper.getMainLooper());

      @Override public void execute(Runnable r) {
        handler.post(r);
      }
    }
  }

// --------------------------------------------------------------------------

// Retrofit.java Retrofit初始化仅保存了平台信息
    Builder(Platform platform) {
      this.platform = platform;
    }

// 然后是baseUrl方法
    /**
     * Set the API base URL.
     *
     * @see #baseUrl(HttpUrl)
     */
    public Builder baseUrl(String baseUrl) {
      checkNotNull(baseUrl, "baseUrl == null");
      return baseUrl(HttpUrl.get(baseUrl));
    }
// 对baseUrl的格式进行判断，必须以 / 结尾，否则抛出异常
    public Builder baseUrl(HttpUrl baseUrl) {
      checkNotNull(baseUrl, "baseUrl == null");
      List<String> pathSegments = baseUrl.pathSegments();
      if (!"".equals(pathSegments.get(pathSegments.size() - 1))) {
        throw new IllegalArgumentException("baseUrl must end in /: " + baseUrl);
      }
      this.baseUrl = baseUrl;
      return this;
    }

// 接下来是addConverterFactory方法，看起没有什么复杂的功能，只是将Converter.Factory的实现加入了list中，
// 我们稍后再看GsonConverterFactory的源码
    private final List<Converter.Factory> converterFactories = new ArrayList<>();

    /** Add converter factory for serialization and deserialization of objects. */
    public Builder addConverterFactory(Converter.Factory factory) {
      converterFactories.add(checkNotNull(factory, "factory == null"));
      return this;
    }

// 最后是build方法
    /**
     * Create the {@link Retrofit} instance using the configured values.
     * <p>
     * Note: If neither {@link #client} nor {@link #callFactory} is called a default {@link
     * OkHttpClient} will be created and used.
     */
    public Retrofit build() {
      if (baseUrl == null) {
        throw new IllegalStateException("Base URL required.");
      }
      // 注意这里初始化了一个OkHttpClient对象
      okhttp3.Call.Factory callFactory = this.callFactory;
      if (callFactory == null) {
        callFactory = new OkHttpClient();
      }

      Executor callbackExecutor = this.callbackExecutor;
      if (callbackExecutor == null) {
        // 我们知道默认情况下，在Android平台，这个callbackExecutor是主线程的Executor
        callbackExecutor = platform.defaultCallbackExecutor();
      }

      // Make a defensive copy of the adapters and add the default Call adapter.
      // callAdapterFactories包括通过Retrofit初始化调用addCallAdapterFactory加入的CallAdapter.Factory，
      // 还包括Android平台默认的platform.defaultCallAdapterFactories
      List<CallAdapter.Factory> callAdapterFactories = new ArrayList<>(this.callAdapterFactories);
      callAdapterFactories.addAll(platform.defaultCallAdapterFactories(callbackExecutor));

      // Make a defensive copy of the converters.
      // converterFactories同理，但是多一个BuiltInConverters，暂时不去管不同的Converter的具体实现
      List<Converter.Factory> converterFactories = new ArrayList<>(
          1 + this.converterFactories.size() + platform.defaultConverterFactoriesSize());

      // Add the built-in converter factory first. This prevents overriding its behavior but also
      // ensures correct behavior when using converters that consume all types.
      converterFactories.add(new BuiltInConverters());
      converterFactories.addAll(this.converterFactories);
      converterFactories.addAll(platform.defaultConverterFactories());
      // 最后完成了Retrofit对象的初始化，引入了几个参数，包括OkHttpClient对象，baseUrl，CallAdapter，
      // Converter以及Executor，validateEagerly默认为false
      return new Retrofit(callFactory, baseUrl, unmodifiableList(converterFactories),
          unmodifiableList(callAdapterFactories), callbackExecutor, validateEagerly);
    }
```

接下来是`Api api = retrofit.create(Api.class);`，Retrofit通过调用create方法将接口类实例化

```java
  @SuppressWarnings("unchecked") // Single-interface proxy creation guarded by parameter safety.
  public <T> T create(final Class<T> service) {
    // validateServiceInterface主要判断service是否为接口且没有继承自其他接口
    Utils.validateServiceInterface(service);
    // validateEagerly为false
    if (validateEagerly) {
      eagerlyValidateMethods(service);
    }
    // 通过代理的方式反射接口，将其实例化
    return (T) Proxy.newProxyInstance(service.getClassLoader(), new Class<?>[] { service },
        new InvocationHandler() {
          // 这里不同的平台有不同的方式
          private final Platform platform = Platform.get();
          private final Object[] emptyArgs = new Object[0];

          @Override public @Nullable Object invoke(Object proxy, Method method,
              @Nullable Object[] args) throws Throwable {
            // If the method is a method from Object then defer to normal invocation.
            // 这里的invoke，Object方法都走这里，比如equals、toString、hashCode什么的
            if (method.getDeclaringClass() == Object.class) {
              return method.invoke(this, args);
            }
            // 如果是Java Web项目则通过platform.invokeDefaultMethod
            if (platform.isDefaultMethod(method)) {
              return platform.invokeDefaultMethod(method, service, proxy, args);
            }
            // 如果是Android则通过loadServiceMethod
            return loadServiceMethod(method).invoke(args != null ? args : emptyArgs);
          }
        });
  }

  private void eagerlyValidateMethods(Class<?> service) {
    Platform platform = Platform.get();
    for (Method method : service.getDeclaredMethods()) {
      if (!platform.isDefaultMethod(method) && !Modifier.isStatic(method.getModifiers())) {
        loadServiceMethod(method);
      }
    }
  }

  ServiceMethod<?> loadServiceMethod(Method method) {
    ServiceMethod<?> result = serviceMethodCache.get(method);
    if (result != null) return result;
    // 默认result为空，通过单例模式取result，简而言之就是得到接口里面定义的方法
    // 并且在方法被调用的时候将参数传入，从而得到结果
    synchronized (serviceMethodCache) {
      result = serviceMethodCache.get(method);
      if (result == null) {
        // 
        result = ServiceMethod.parseAnnotations(this, method);
        serviceMethodCache.put(method, result);
      }
    }
    return result;
  }

// --------------------------------------------------------------------------

// ServiceMethod.java
abstract class ServiceMethod<T> {
  // parseAnnotations还是通过RequestFactory解析接口的方法，因为我们定义的方法是包含注解的，所以必定需要通过
  // 解析注解的值来控制方法的参数
  static <T> ServiceMethod<T> parseAnnotations(Retrofit retrofit, Method method) {
    // RequestFactory看名字就知道应该和构建HTTP请求相关，应该是将retrofit定义的baseUrl等信息以及接口定义的方法，
    // 包括注解里的信息整合
    RequestFactory requestFactory = RequestFactory.parseAnnotations(retrofit, method);

    Type returnType = method.getGenericReturnType();
    if (Utils.hasUnresolvableType(returnType)) {
      throw methodError(method,
          "Method return type must not include a type variable or wildcard: %s", returnType);
    }
    if (returnType == void.class) {
      throw methodError(method, "Service methods cannot return void.");
    }
    // HttpServiceMethod继承自ServiceMethod，实现invoke方法，即最终我们调用接口中的方式时将参数传入
    return HttpServiceMethod.parseAnnotations(retrofit, method, requestFactory);
  }

  abstract @Nullable T invoke(Object[] args);
}

// --------------------------------------------------------------------------

// RequestFactory.java
  static RequestFactory parseAnnotations(Retrofit retrofit, Method method) {
    return new Builder(retrofit, method).build();
  }
  
    // build方法构建的实例
    RequestFactory build() {
      for (Annotation annotation : methodAnnotations) {
        // 在parseMethodAnnotation中处理接口方法的注解，这里仅保存了请求方法以及
        // 方法注解中的value
        parseMethodAnnotation(annotation);
      }

      if (httpMethod == null) {
        throw methodError(method, "HTTP method annotation is required (e.g., @GET, @POST, etc.).");
      }

      if (!hasBody) {
        if (isMultipart) {
          throw methodError(method,
              "Multipart can only be specified on HTTP methods with request body (e.g., @POST).");
        }
        if (isFormEncoded) {
          throw methodError(method, "FormUrlEncoded can only be specified on HTTP methods with "
              + "request body (e.g., @POST).");
        }
      }
      // parameterAnnotationsArray是通过Method传过来的，简单来说就是方法的参数注解，
      // 即我们使用的@Query("location")和@Query("key")
      int parameterCount = parameterAnnotationsArray.length;
      parameterHandlers = new ParameterHandler<?>[parameterCount];
      for (int p = 0, lastParameter = parameterCount - 1; p < parameterCount; p++) {
        // 通过parseParameter方法处理参数注解，并保存在parameterHandlers中
        parameterHandlers[p] =
            parseParameter(p, parameterTypes[p], parameterAnnotationsArray[p], p == lastParameter);
      }

      if (relativeUrl == null && !gotUrl) {
        throw methodError(method, "Missing either @%s URL or @Url parameter.", httpMethod);
      }
      if (!isFormEncoded && !isMultipart && !hasBody && gotBody) {
        throw methodError(method, "Non-body HTTP method cannot contain @Body.");
      }
      if (isFormEncoded && !gotField) {
        throw methodError(method, "Form-encoded method must contain at least one @Field.");
      }
      if (isMultipart && !gotPart) {
        throw methodError(method, "Multipart method must contain at least one @Part.");
      }

      return new RequestFactory(this);
    }
    // parseMethodAnnotation处理的是方法注解即 @GET("now?") ，now?作为value
    // 根据不同的注解类型，构造不同的请求方法
    private void parseMethodAnnotation(Annotation annotation) {
      if (annotation instanceof DELETE) {
        parseHttpMethodAndPath("DELETE", ((DELETE) annotation).value(), false);
      } else if (annotation instanceof GET) {
        parseHttpMethodAndPath("GET", ((GET) annotation).value(), false);
      } else if (annotation instanceof HEAD) {
        parseHttpMethodAndPath("HEAD", ((HEAD) annotation).value(), false);
      } else if (annotation instanceof PATCH) {
        parseHttpMethodAndPath("PATCH", ((PATCH) annotation).value(), true);
      } else if (annotation instanceof POST) {
        parseHttpMethodAndPath("POST", ((POST) annotation).value(), true);
      } else if (annotation instanceof PUT) {
        parseHttpMethodAndPath("PUT", ((PUT) annotation).value(), true);
      } else if (annotation instanceof OPTIONS) {
        parseHttpMethodAndPath("OPTIONS", ((OPTIONS) annotation).value(), false);
      } else if (annotation instanceof HTTP) {
        HTTP http = (HTTP) annotation;
        parseHttpMethodAndPath(http.method(), http.path(), http.hasBody());
      } else if (annotation instanceof retrofit2.http.Headers) {
        String[] headersToParse = ((retrofit2.http.Headers) annotation).value();
        if (headersToParse.length == 0) {
          throw methodError(method, "@Headers annotation is empty.");
        }
        headers = parseHeaders(headersToParse);
      } else if (annotation instanceof Multipart) {
        if (isFormEncoded) {
          throw methodError(method, "Only one encoding annotation is allowed.");
        }
        isMultipart = true;
      } else if (annotation instanceof FormUrlEncoded) {
        if (isMultipart) {
          throw methodError(method, "Only one encoding annotation is allowed.");
        }
        isFormEncoded = true;
      }
    }

    private void parseHttpMethodAndPath(String httpMethod, String value, boolean hasBody) {
      if (this.httpMethod != null) {
        throw methodError(method, "Only one HTTP method is allowed. Found: %s and %s.",
            this.httpMethod, httpMethod);
      }
      // 保存了请求方法
      this.httpMethod = httpMethod;
      this.hasBody = hasBody;

      if (value.isEmpty()) {
        return;
      }

      // Get the relative URL path and existing query string, if present.
      // 这里的判断是确保@GET("now?location={location}&key={key}")其中的location={location}&key={key}不会出现，
      // 因为需要通过@Query注解构建，所以这里不允许使用
      int question = value.indexOf('?');
      if (question != -1 && question < value.length() - 1) {
        // Ensure the query string does not have any named parameters.
        String queryParams = value.substring(question + 1);
        Matcher queryParamMatcher = PARAM_URL_REGEX.matcher(queryParams);
        if (queryParamMatcher.find()) {
          throw methodError(method, "URL query string \"%s\" must not have replace block. "
              + "For dynamic query parameters use @Query.", queryParams);
        }
      }

      this.relativeUrl = value;
      this.relativeUrlParamNames = parsePathParameters(value);
    }    

// parseParameter方法，对于同一个参数似乎可以使用多个参数注解Annotation[] annotations
    private @Nullable ParameterHandler<?> parseParameter(
        int p, Type parameterType, @Nullable Annotation[] annotations, boolean allowContinuation) {
      ParameterHandler<?> result = null;
      if (annotations != null) {
        for (Annotation annotation : annotations) {
          // 调用parseParameterAnnotation对参数注解进行处理，其中还包括传入的参数类型parameterType
          ParameterHandler<?> annotationAction =
              parseParameterAnnotation(p, parameterType, annotations, annotation);

          if (annotationAction == null) {
            continue;
          }

          if (result != null) {
            throw parameterError(method, p,
                "Multiple Retrofit annotations found, only one allowed.");
          }

          result = annotationAction;
        }
      }

      if (result == null) {
        if (allowContinuation) {
          try {
            if (Utils.getRawType(parameterType) == Continuation.class) {
              isKotlinSuspendFunction = true;
              return null;
            }
          } catch (NoClassDefFoundError ignored) {
          }
        }
        throw parameterError(method, p, "No Retrofit annotation found.");
      }

      return result;
    }

// parseParameterAnnotation方法，这里判断参数注解的类型，我们只看@Query
    @Nullable
    private ParameterHandler<?> parseParameterAnnotation(
        int p, Type type, Annotation[] annotations, Annotation annotation) {
      if (annotation instanceof Url) {
        // ...

      } else if (annotation instanceof Path) {
        // ...

      } else if (annotation instanceof Query) {
        validateResolvableType(p, type);
        Query query = (Query) annotation;
        String name = query.value();
        boolean encoded = query.encoded();

        Class<?> rawParameterType = Utils.getRawType(type);
        gotQuery = true;
        // 判断参数类型是否为可迭代类或者Array类，目前我们的参数是String，所以直接到最后一个条件
        if (Iterable.class.isAssignableFrom(rawParameterType)) {
          if (!(type instanceof ParameterizedType)) {
            throw parameterError(method, p, rawParameterType.getSimpleName()
                + " must include generic type (e.g., "
                + rawParameterType.getSimpleName()
                + "<String>)");
          }
          ParameterizedType parameterizedType = (ParameterizedType) type;
          Type iterableType = Utils.getParameterUpperBound(0, parameterizedType);
          Converter<?, String> converter =
              retrofit.stringConverter(iterableType, annotations);
          return new ParameterHandler.Query<>(name, converter, encoded).iterable();
        } else if (rawParameterType.isArray()) {
          Class<?> arrayComponentType = boxIfPrimitive(rawParameterType.getComponentType());
          Converter<?, String> converter =
              retrofit.stringConverter(arrayComponentType, annotations);
          return new ParameterHandler.Query<>(name, converter, encoded).array();
        } else {
          // 这里调用了retrofit.stringConverter方法，将参数类型和注解进行处理，
          // 这里ParameterHandler.Query<>保存了参数注解的value、Converter以及参数注解的编码方式
          Converter<?, String> converter =
              retrofit.stringConverter(type, annotations);
          return new ParameterHandler.Query<>(name, converter, encoded);
        }

      } 
      // ...
      return null; // Not a Retrofit annotation.
    }

// --------------------------------------------------------------------------

// Retrofit.java stringConverter通过遍历converterFactories，调用它们的stringConverter方法，
// 看谁能够处理并返回一个Converter<T, String>，如果都没有则调用BuiltInConverters，
// 而Converter是用于构造HTTP请求
  /**
   * Returns a {@link Converter} for {@code type} to {@link String} from the available
   * {@linkplain #converterFactories() factories}.
   */
  public <T> Converter<T, String> stringConverter(Type type, Annotation[] annotations) {
    checkNotNull(type, "type == null");
    checkNotNull(annotations, "annotations == null");

    for (int i = 0, count = converterFactories.size(); i < count; i++) {
      Converter<?, String> converter =
          converterFactories.get(i).stringConverter(type, annotations, this);
      if (converter != null) {
        //noinspection unchecked
        return (Converter<T, String>) converter;
      }
    }

    // Nothing matched. Resort to default converter which just calls toString().
    //noinspection unchecked
    return (Converter<T, String>) BuiltInConverters.ToStringConverter.INSTANCE;
  }
```

以上的代码完成了RequestFactory的构建，也就是说，这个RequestFactory包含了HTTP请求的部分信息，比如请求方法、请求url的参数、参数类型以及参数的位置，通过`HttpServiceMethod.parseAnnotations(retrofit, method, requestFactory);`对请求进行适配，包括通过Converter对返回的Response body数据处理以及通过CallAdapter修改Call类型

```java
// HttpServiceMethod.java HttpServiceMethod继承自ServiceMethod
  /**
   * Inspects the annotations on an interface method to construct a reusable service method that
   * speaks HTTP. This requires potentially-expensive reflection so it is best to build each service
   * method only once and reuse it.
   */
  static <ResponseT, ReturnT> HttpServiceMethod<ResponseT, ReturnT> parseAnnotations(
      Retrofit retrofit, Method method, RequestFactory requestFactory) {
    boolean isKotlinSuspendFunction = requestFactory.isKotlinSuspendFunction;
    boolean continuationWantsResponse = false;
    boolean continuationBodyNullable = false;

    Annotation[] annotations = method.getAnnotations();
    Type adapterType;
    if (isKotlinSuspendFunction) {
      Type[] parameterTypes = method.getGenericParameterTypes();
      Type responseType = Utils.getParameterLowerBound(0,
          (ParameterizedType) parameterTypes[parameterTypes.length - 1]);
      if (getRawType(responseType) == Response.class && responseType instanceof ParameterizedType) {
        // Unwrap the actual body type from Response<T>.
        responseType = Utils.getParameterUpperBound(0, (ParameterizedType) responseType);
        continuationWantsResponse = true;
      } else {
        // TODO figure out if type is nullable or not
        // Metadata metadata = method.getDeclaringClass().getAnnotation(Metadata.class)
        // Find the entry for method
        // Determine if return type is nullable or not
      }

      adapterType = new Utils.ParameterizedTypeImpl(null, Call.class, responseType);
      annotations = SkipCallbackExecutorImpl.ensurePresent(annotations);
    } else {
      adapterType = method.getGenericReturnType();
    }

    CallAdapter<ResponseT, ReturnT> callAdapter =
        createCallAdapter(retrofit, method, adapterType, annotations);
    Type responseType = callAdapter.responseType();
    if (responseType == okhttp3.Response.class) {
      throw methodError(method, "'"
          + getRawType(responseType).getName()
          + "' is not a valid response body type. Did you mean ResponseBody?");
    }
    if (responseType == Response.class) {
      throw methodError(method, "Response must include generic type (e.g., Response<String>)");
    }
    // TODO support Unit for Kotlin?
    if (requestFactory.httpMethod.equals("HEAD") && !Void.class.equals(responseType)) {
      throw methodError(method, "HEAD method must use Void as response type.");
    }

    Converter<ResponseBody, ResponseT> responseConverter =
        createResponseConverter(retrofit, method, responseType);

    okhttp3.Call.Factory callFactory = retrofit.callFactory;
    // isKotlinSuspendFunction和continuationWantsResponse默认为false，所以返回的是SuspendForBody
    if (!isKotlinSuspendFunction) {
      return new CallAdapted<>(requestFactory, callFactory, responseConverter, callAdapter);
    } else if (continuationWantsResponse) {
      //noinspection unchecked Kotlin compiler guarantees ReturnT to be Object.
      return (HttpServiceMethod<ResponseT, ReturnT>) new SuspendForResponse<>(requestFactory,
          callFactory, responseConverter, (CallAdapter<ResponseT, Call<ResponseT>>) callAdapter);
    } else {
      //noinspection unchecked Kotlin compiler guarantees ReturnT to be Object.
      return (HttpServiceMethod<ResponseT, ReturnT>) new SuspendForBody<>(requestFactory,
          callFactory, responseConverter, (CallAdapter<ResponseT, Call<ResponseT>>) callAdapter,
          continuationBodyNullable);
    }
  }

// Retrofit的create方法调用了loadServiceMethod(method).invoke(args != null ? args : emptyArgs);
// 此处的invoke即HttpServiceMethod的invoke方法，这里创建了OkHttpCall，
// 此处的adapt即SuspendForBody的adapt方法，而SuspendForBody的adapt方法调用了callAdapter的adapt方法，
// 最终回到了我们在Retrofit初始化时使用的DefaultCallAdapterFactory的adapt方法，如果我们使用其他callAdapter，
// 比如RxJava2CallAdapterFactory，那么返回值就是RxJava2CallAdapterFactory的adapt方法的返回值
  @Override final @Nullable ReturnT invoke(Object[] args) {
    Call<ResponseT> call = new OkHttpCall<>(requestFactory, args, callFactory, responseConverter);
    return adapt(call, args);
  }
```

```java
// DefaultCallAdapterFactory.java 返回了一个Call ExecutorCallbackCall
      @Override public Call<Object> adapt(Call<Object> call) {
        return executor == null
            ? call
            : new ExecutorCallbackCall<>(executor, call);
      }

  static final class ExecutorCallbackCall<T> implements Call<T> {
    final Executor callbackExecutor;
    final Call<T> delegate;

    ExecutorCallbackCall(Executor callbackExecutor, Call<T> delegate) {
      this.callbackExecutor = callbackExecutor;
      this.delegate = delegate;
    }
// ExecutorCallbackCall是通过callbackExecutor执行Runnable，还记得在Platform类中的Android内部类的默认Executor吗，
// MainThreadExecutor，所以后续调用call.enqueue时都是在这里处理的，而且delegate为OkHttpCall，OkHttpCall执行enqueue
    @Override public void enqueue(final Callback<T> callback) {
      checkNotNull(callback, "callback == null");

      delegate.enqueue(new Callback<T>() {
        @Override public void onResponse(Call<T> call, final Response<T> response) {
          callbackExecutor.execute(new Runnable() {
            @Override public void run() {
              if (delegate.isCanceled()) {
                // Emulate OkHttp's behavior of throwing/delivering an IOException on cancellation.
                callback.onFailure(ExecutorCallbackCall.this, new IOException("Canceled"));
              } else {
                callback.onResponse(ExecutorCallbackCall.this, response);
              }
            }
          });
        }

        @Override public void onFailure(Call<T> call, final Throwable t) {
          callbackExecutor.execute(new Runnable() {
            @Override public void run() {
              callback.onFailure(ExecutorCallbackCall.this, t);
            }
          });
        }
      });
    }

    @Override public boolean isExecuted() {
      return delegate.isExecuted();
    }

    @Override public Response<T> execute() throws IOException {
      return delegate.execute();
    }

    @Override public void cancel() {
      delegate.cancel();
    }

    @Override public boolean isCanceled() {
      return delegate.isCanceled();
    }

    @SuppressWarnings("CloneDoesntCallSuperClone") // Performing deep clone.
    @Override public Call<T> clone() {
      return new ExecutorCallbackCall<>(callbackExecutor, delegate.clone());
    }

    @Override public Request request() {
      return delegate.request();
    }
  }
```

通过上述代码，`Api api = retrofit.create(Api.class);`主要还是通过代理反射创建了Api接口的实例，后续直接调用`api.getNowWeather("beijing", KEY);`就可以构造一个Call对象；在retrofit.create的过程中需要通过ServiceMethod以及初始化的Retrofit对象对Method的注解进行解析，转换为HttpServiceMethod对象进行请求适配，包括处理response body数据以及修改Call类型等等，然后构建OkHttpCall，返回ExecutorCallbackCall，所以后续OkHttpCall的enqueue方法可以进行回调。

```java
// OkHttpCall.java 继承自Call，这里执行的代码非常类似OkHttp的RealCall类
  @Override public void enqueue(final Callback<T> callback) {
    checkNotNull(callback, "callback == null");

    okhttp3.Call call;
    Throwable failure;

    synchronized (this) {
      if (executed) throw new IllegalStateException("Already executed.");
      executed = true;

      call = rawCall;
      failure = creationFailure;
      if (call == null && failure == null) {
        try {
          // 我们需要把this，也就是OkHttpCall转换为OkHttpClient接受的Call，所以需要OkHttp的callFactory
          call = rawCall = createRawCall();
        } catch (Throwable t) {
          throwIfFatal(t);
          failure = creationFailure = t;
        }
      }
    }

    if (failure != null) {
      callback.onFailure(this, failure);
      return;
    }

    if (canceled) {
      call.cancel();
    }
// 这里就直接使用了OkHttp的enqueue方法，然后再onResponse中处理rawResponse，
// 通过parseResponse将返回的response body转为我们定义的数据，比如json->WeatherEntity
// 所以回调函数的结果包括Response<WeatherEntity>
    call.enqueue(new okhttp3.Callback() {
      @Override public void onResponse(okhttp3.Call call, okhttp3.Response rawResponse) {
        Response<T> response;
        try {
          response = parseResponse(rawResponse);
        } catch (Throwable e) {
          throwIfFatal(e);
          callFailure(e);
          return;
        }

        try {
          // 回调函数传出去
          callback.onResponse(OkHttpCall.this, response);
        } catch (Throwable t) {
          throwIfFatal(t);
          t.printStackTrace(); // TODO this is not great
        }
      }

      @Override public void onFailure(okhttp3.Call call, IOException e) {
        callFailure(e);
      }

      private void callFailure(Throwable e) {
        try {
          callback.onFailure(OkHttpCall.this, e);
        } catch (Throwable t) {
          throwIfFatal(t);
          t.printStackTrace(); // TODO this is not great
        }
      }
    });
  }

// 将Call转换为OkHttp的Call，requestFactory.create(args)会构造RequestBuilder，
// RequestBuilder就是将我们之前保存在各种对象中的参数拿出来组建出一个Http请求，
// callFactory就是OkHttpClient对象
  private okhttp3.Call createRawCall() throws IOException {
    okhttp3.Call call = callFactory.newCall(requestFactory.create(args));
    if (call == null) {
      throw new NullPointerException("Call.Factory returned null.");
    }
    return call;
  }


  Response<T> parseResponse(okhttp3.Response rawResponse) throws IOException {
    ResponseBody rawBody = rawResponse.body();

    // Remove the body's source (the only stateful object) so we can pass the response along.
    rawResponse = rawResponse.newBuilder()
        .body(new NoContentResponseBody(rawBody.contentType(), rawBody.contentLength()))
        .build();

    int code = rawResponse.code();
    if (code < 200 || code >= 300) {
      try {
        // Buffer the entire body to avoid future I/O.
        ResponseBody bufferedBody = Utils.buffer(rawBody);
        return Response.error(bufferedBody, rawResponse);
      } finally {
        rawBody.close();
      }
    }

    if (code == 204 || code == 205) {
      rawBody.close();

      return Response.success(null, rawResponse);
    }
// 一般来说数据请求正确，返回code为200，因此走这条路，注意responseConverter.convert，也就是我们使用的
// 再Retrofit初始化的converterFactories，包括我们加入的GsonConverterFactory，最终Response的body被转换为
// WeatherEntity
    ExceptionCatchingResponseBody catchingBody = new ExceptionCatchingResponseBody(rawBody);
    try {
      T body = responseConverter.convert(catchingBody);
      return Response.success(body, rawResponse);
    } catch (RuntimeException e) {
      // If the underlying source threw an exception, propagate that rather than indicating it was
      // a runtime exception.
      catchingBody.throwIfCaught();
      throw e;
    }
  }  

// --------------------------------------------------------------------------

// GsonConverterFactory.java 提供GsonResponseBodyConverter给Retrofit对Response进行数据转换
public final class GsonConverterFactory extends Converter.Factory {
  /**
   * Create an instance using a default {@link Gson} instance for conversion. Encoding to JSON and
   * decoding from JSON (when no charset is specified by a header) will use UTF-8.
   */
  public static GsonConverterFactory create() {
    return create(new Gson());
  }

  /**
   * Create an instance using {@code gson} for conversion. Encoding to JSON and
   * decoding from JSON (when no charset is specified by a header) will use UTF-8.
   */
  @SuppressWarnings("ConstantConditions") // Guarding public API nullability.
  public static GsonConverterFactory create(Gson gson) {
    if (gson == null) throw new NullPointerException("gson == null");
    return new GsonConverterFactory(gson);
  }

  private final Gson gson;

  private GsonConverterFactory(Gson gson) {
    this.gson = gson;
  }
// responseBodyConverter被调用的位置是HttpServiceMethod的createResponseConverter
  @Override
  public Converter<ResponseBody, ?> responseBodyConverter(Type type, Annotation[] annotations,
      Retrofit retrofit) {
    TypeAdapter<?> adapter = gson.getAdapter(TypeToken.get(type));
    return new GsonResponseBodyConverter<>(gson, adapter);
  }
// requestBodyConverter被调用的位置在RequestFactory的parseParameterAnnotation
  @Override
  public Converter<?, RequestBody> requestBodyConverter(Type type,
      Annotation[] parameterAnnotations, Annotation[] methodAnnotations, Retrofit retrofit) {
    TypeAdapter<?> adapter = gson.getAdapter(TypeToken.get(type));
    return new GsonRequestBodyConverter<>(gson, adapter);
  }
}

// GsonResponseBodyConverter.java 
final class GsonResponseBodyConverter<T> implements Converter<ResponseBody, T> {
  private final Gson gson;
  private final TypeAdapter<T> adapter;

  GsonResponseBodyConverter(Gson gson, TypeAdapter<T> adapter) {
    this.gson = gson;
    this.adapter = adapter;
  }
// convert方法被执行的位置，也就是说通过TypeAdapter读取json数据并转换为java对象，这个具体实现需要分析Gson的源码
  @Override public T convert(ResponseBody value) throws IOException {
    JsonReader jsonReader = gson.newJsonReader(value.charStream());
    try {
      T result = adapter.read(jsonReader);
      if (jsonReader.peek() != JsonToken.END_DOCUMENT) {
        throw new JsonIOException("JSON document was not fully consumed.");
      }
      return result;
    } finally {
      value.close();
    }
  }
}
```

除了GsonConverterFactory，还可以分析一下RxJava2CallAdapterFactory，我们知道HttpServiceMethod的invoke返回的对象即为我们调用`api.getNowWeather("beijing", KEY);`得到的对象，而这个对象是通过callAdapter调用adapt方法返回的，默认情况下是DefaultCallAdapterFactory，如果我们在Retrofit初始化时通过addCallAdapterFactory增加了其他的CallAdapterFactory比如RxJava2CallAdapterFactory，那么会通过RxJava2CallAdapterFactory调用RxJava2CallAdapter的adapt方法

```java 
// RxJava2CallAdapterFactory.java RxJava2CallAdapterFactory的get方法必定返回RxJava2CallAdapter对象
  public static RxJava2CallAdapterFactory create() {
    return new RxJava2CallAdapterFactory(null, false);
  }

  private RxJava2CallAdapterFactory(@Nullable Scheduler scheduler, boolean isAsync) {
    this.scheduler = scheduler;
    this.isAsync = isAsync;
  }

// RxJava2CallAdapter.java 所以具体的adapt方法由RxJava2CallAdapter实现
  @Override public Object adapt(Call<R> call) {
    // 主要请求的完成过程在CallEnqueueObservable中，异步的
    Observable<Response<R>> responseObservable = isAsync
        ? new CallEnqueueObservable<>(call)
        : new CallExecuteObservable<>(call);

    Observable<?> observable;
    // ResultObservable和BodyObservable都是继承自Observable，用于返回结果
    if (isResult) {
      observable = new ResultObservable<>(responseObservable);
    } else if (isBody) {
      observable = new BodyObservable<>(responseObservable);
    } else {
      observable = responseObservable;
    }

    if (scheduler != null) {
      observable = observable.subscribeOn(scheduler);
    }

    if (isFlowable) {
      return observable.toFlowable(BackpressureStrategy.LATEST);
    }
    if (isSingle) {
      return observable.singleOrError();
    }
    if (isMaybe) {
      return observable.singleElement();
    }
    if (isCompletable) {
      return observable.ignoreElements();
    }
    return RxJavaPlugins.onAssembly(observable);
  }

// CallEnqueueObservable.java 当我们得到的observable执行subscribe方法时
// 实际调用了subscribeActual方法，对应上面的CallEnqueueObservable
  @Override protected void subscribeActual(Observer<? super Response<T>> observer) {
    // Since Call is a one-shot type, clone it for each new observer.
    Call<T> call = originalCall.clone();
    CallCallback<T> callback = new CallCallback<>(call, observer);
    observer.onSubscribe(callback);
    if (!callback.isDisposed()) {
      // 这个call是在HttpServiceMethod中构建的OkHttpCall，OkHttpCall调用enqueue不必多说了吧
      call.enqueue(callback);
    }
  }
```

综上所述，Retrofit是一个比较灵活的网络请求框架，从设计上就是为了便于增加其他组件而设计的，首先是Api接口的设计，为了更加方便控制请求参数，通过接口加注解设计请求的url，而同时我们又不必实现此接口，通过代理反射的方式对接口实体化，相当于解耦了请求url与Retrofit实例；

其次是CallAdapter的设计，我们可以灵活的设计自己的CallAdapter用于同步或异步请求，因为在HttpServiceMethod被调用的时候是通过获取Retrofit初始化时设置的CallAdapter来实现返回，所以只需要自定义CallAdapter，我们就可以按照自己的需求处理请求的过程并拿到返回值；

然后是与Gson的联动，在拿到返回Response的时候，对json数据进行转换，并且将实体通过回调传出来，都是为了灵活使用而设计的；

最后是Retrofit与OkHttp的结合，Retrofit本质上还是调用OkHttp的请求，但是通过上述方式增加其灵活性，而且由于OkHttpCall的连接，我们一方面可以直接使用OkHttpClient，另一方面返回的Response可以直接处理，其中又包括非常多的泛型，这种设计思路真是妙啊妙啊。







