


参考：

> [Android Handler 消息机制详述](https://www.jianshu.com/p/1a5a3db45cfa)
> [Rxjava这一篇就够了，墙裂推荐](https://juejin.im/post/5a224cc76fb9a04527256683)

Android中很多地方都需要跨线程通信，这是由于Android主线程不允许进行复杂的网络请求或者其他非常耗时的操作，否则会导致ANR，主线程只能进行UI操作，比如修改某个控件的text、设置某个控件不可见等等，因此网络请求等操作需要在其他线程中完成，当数据在其他线程中获取完毕时，通过跨线程通信将数据传到主线程中，主线程就可以直接根据数据进行UI操作。常见的跨线程通信的方式有Handler、AsyncTask、EventBus以及RxJava等，前两个是Android自带，后两者是封装好的第三方库。

## 1. Handler

Handler是Android中最简单的线程间通信方式，同时也可以在同一个线程中发送消息，但是使用时需要注意内存泄漏的问题。

### 1.1 Handler简单使用

还是以和风天气请求为例，我们的目标是在子线程中请求数据，然后通过Handler将数据传到主线程中并显示出来。

```java
public class MainActivity extends AppCompatActivity {
    private final static String KEY = "XXXXXXXXXX";
    private final static String URL = "https://free-api.heweather.net/s6/weather/";

    private TextView textView;
    private Handler handler;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        textView = findViewById(R.id.textView);
        // Handler的实例化，重写handleMessage方法用于等待处理msg，
        // handleMessage方法是回调，在回调中更新UI，此时执行在主线程，
        // 在Android Studio中会提示这里存在内存泄漏问题
        handler = new Handler() {
            @Override
            public void handleMessage(Message msg) {
                super.handleMessage(msg);
                textView.setText(msg.obj.toString());
            }
        };
        // 在子线程开启一个网络请求
        new Thread(new Runnable() {
            @Override
            public void run() {
                // Retrofit通用代码
                Retrofit retrofit = new Retrofit.Builder()
                        .baseUrl(URL) // 设置网络请求的公共Url地址
                        .addConverterFactory(GsonConverterFactory.create()) // 设置数据解析器
                        .build();

                Api api = retrofit.create(Api.class);
                Call<WeatherEntity> call = api.getNowWeather("beijing", KEY);
                try {
                    // 为了在当前子线程获取数据，这里直接使用execute
                    WeatherEntity result = call.execute().body();
                    // Message的实例化方法Message.obtain
                    Message message = Message.obtain();
                    // 可以通过Message附加很多数据，这里仅用obj，保存我们网络请求得到的实例
                    message.obj = result;
                    // 通过handler.sendMessage(message)实现调用回调方法，完成数据传输
                    // 这种操作有点类似于接口回调
                    handler.sendMessage(message);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }
}
```

这里的内存泄露的原因可以参考其他资料，主要是**Java 中非静态内部类和匿名内部类会持有外部类的引用**同时**Handler 的生命周期比外部类长**导致的。如何解决，肯定就是让Handler是静态内部类就完事了

```java
public class MainActivity extends AppCompatActivity {
    private final static String KEY = "XXXXXXXXXX";
    private final static String URL = "https://free-api.heweather.net/s6/weather/";

    private TextView textView;
    private Handler handler;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        textView = findViewById(R.id.textView);
        // 使用自定义的静态内部类
        handler = new MyHandler(this);
        // 子线程请求没有变化
        new Thread(new Runnable() { 
            @Override
            public void run() {
                Retrofit retrofit = new Retrofit.Builder()
                        .baseUrl(URL) // 设置网络请求的公共Url地址
                        .addConverterFactory(GsonConverterFactory.create()) // 设置数据解析器
                        .build();

                Api api = retrofit.create(Api.class);
                Call<WeatherEntity> call = api.getNowWeather("beijing", KEY);
                try {
                    WeatherEntity result = call.execute().body();
                    Message message = Message.obtain();
                    message.obj = result;
                    handler.sendMessage(message);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }

    @Override
    protected void onDestroy() {
        handler.removeCallbacksAndMessages(null);
        super.onDestroy();
    }
    // 
    public void handleMessage(Message msg) {
        textView.setText(msg.obj.toString());
    }
    // 自定义静态内部类，与onDestroy中removeCallbacksAndMessages一起使用
    public static class MyHandler extends Handler {
        private WeakReference<MainActivity> reference;

        public MyHandler(MainActivity mainActivity) {
            // 同时需要持有对MainActivity的弱引用
            this.reference = new WeakReference<>(mainActivity);
        }

        @Override
        public void handleMessage(Message msg) {
            super.handleMessage(msg);
            MainActivity mainActivity = reference.get();
            if (mainActivity != null) {
                // 将msg传给MainActivity处理
                mainActivity.handleMessage(msg);
            }
        }
    }
}
```

### 1.2 Handler线程间通信

上面的例子仅演示了从子线程传数据给主线程，那么如果同时需要从主线程传数据给子线程，怎么办

```java
// 首先需要自定义MyThread，完成Looper的初始化，否则子线程不会自动初始化Looper
    private class MyThread extends Thread {
        private Looper looper;

        @Override
        public void run() {
            super.run();
            Looper.prepare();
            looper = Looper.myLooper();
            Looper.loop();
        }
    }

// 然后在onCreate方法中
    Log.i("aaaa", String.valueOf(Thread.currentThread()));
    MyThread thread = new MyThread();
    thread.start(); // 必须先启动子线程
    while (true) {
        // 确保子线程中的Looper初始化完成
        if (thread.looper != null) {
            // 此时handler的handleMessage方法是在子线程MyThread中执行的
            // 两处log中线程的值是不一样的，通过Handler的构造方法实现子线程的调用
            handler = new Handler(thread.looper) {
                @Override
                public void handleMessage(Message msg) {
                    Log.i("aaaa", String.valueOf(msg.what) + Thread.currentThread());
                }
            };
            handler.sendEmptyMessage(12321);
            break;
        }
    }

// 如果使用定义好的HandlerThread，则不需要继承Thread，直接使用，
// HandlerThread默认帮我们完成了Looper的初始化
    Log.i("aaaa", String.valueOf(Thread.currentThread()));
    // HandlerThread需要用String的构造方法，我们在log中也可以看到
    HandlerThread thread = new HandlerThread("new thread");
    thread.start();
    while (true) {
        if (thread.getLooper() != null) {
            handler = new Handler(thread.getLooper()) {
                @Override
                public void handleMessage(Message msg) {
                    Log.i("aaaa", String.valueOf(msg.what) + Thread.currentThread());
                }
            };
            handler.sendEmptyMessage(12321);
            break;
        }
    }
```

> 为什么子线程需要初始化Looper，而主线程不需要？

首先需要明白的是，只有需要处理消息的线程才需要Looper，即哪个线程执行了handleMessage方法，则线程需要Looper，原因在源码分析中解释；主线程以及HandlerThread会自动进行Looper的初始化，而`new Thread()`不会，因此在第二个例子中，子线程需要处理消息，所以需要初始化Looper而第一个例子中主线程不需要。

> Handler的初始化，其构造方法依赖于什么，为什么第二个例子中Handler不是在主线程中初始化的吗？

首先需要知道的是Handler是可以被跨线程调用的，而View是不可以的，举个例子，如果在第一个例子中我们在子线程中调用`textView.setText(result.toString());`，则会报错`CalledFromWrongThreadException: Only the original thread that created a view hierarchy can touch its views.`，而Handler没问题，Handler默认构造方法`new Handler()`会将当前线程的Looper保存在自己这个实例中，即将主线程中的Looper保存，而带参数的构造方法`new Handler(thread.looper)`会保存thread的looper在实例中，又因为Handler是可以跨线程调用的，所以区分Handler属于哪个线程其实是根据构造方法传入的参数决定的，至于Handler归属于不同的线程会有什么影响，在源码分析中解释。

### 1.3 Handler源码分析

以从子线程向主线程发送消息为例





## 2. AsyncTask


## 3. EventBus


## 4. RxJava








