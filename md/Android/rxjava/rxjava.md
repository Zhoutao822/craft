


参考：

> [Android Handler 消息机制详述](https://www.jianshu.com/p/1a5a3db45cfa)
> [Rxjava这一篇就够了，墙裂推荐](https://juejin.im/post/5a224cc76fb9a04527256683)
> [Android中为什么主线程不会因为Looper.loop()里的死循环卡死？](https://www.zhihu.com/question/34652589)

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

以从子线程向主线程发送消息为例，首先从ActivityThread的main方法开始，前面说过主线程中的Looper是自动初始化的，其初始化的位置就在ActivityThread的main方法中

```java
// ActivityThread.java 核心就两个Looper.prepareMainLooper()和Looper.loop()
    public static void main(String[] args) {
      
        // ...

        Looper.prepareMainLooper();

        // ...
        // 显然这里是不会执行的
        if (false) {
            Looper.myLooper().setMessageLogging(new
                    LogPrinter(Log.DEBUG, "ActivityThread"));
        }

        // End of event ActivityThreadMain.
        Trace.traceEnd(Trace.TRACE_TAG_ACTIVITY_MANAGER);
        Looper.loop();

        throw new RuntimeException("Main thread loop unexpectedly exited");
    }
```

再看看Looper.prepareMainLooper()的作用

```java
// Looper.java 看注释就知道是是为主线程初始化Looper，关键还是看prepare方法，再看myLooper
    /**
     * Initialize the current thread as a looper, marking it as an
     * application's main looper. The main looper for your application
     * is created by the Android environment, so you should never need
     * to call this function yourself.  See also: {@link #prepare()}
     */
    public static void prepareMainLooper() {
        prepare(false);
        synchronized (Looper.class) {
            if (sMainLooper != null) {
                throw new IllegalStateException("The main Looper has already been prepared.");
            }
            sMainLooper = myLooper();
        }
    }

// prepare方法通过sThreadLocal set了一个Looper实例，
// 一个Looper实例保存了MessageQueue和Thread.currentThread()
    private static void prepare(boolean quitAllowed) {
        if (sThreadLocal.get() != null) {
            throw new RuntimeException("Only one Looper may be created per thread");
        }
        sThreadLocal.set(new Looper(quitAllowed));
    }

// myLooper方法从sThreadLocal get到Looper，那正好对应上面prepare set的Looper，
// ThreadLocal的作用是可以保存线程内的变量，简而言之就是通过ThreadLocal的set和get方法
// 处理的变量仅属于某个线程，以Looper为例，在某个线程中有且仅有一个
    /**
     * Return the Looper object associated with the current thread.  Returns
     * null if the calling thread is not associated with a Looper.
     */
    public static @Nullable Looper myLooper() {
        return sThreadLocal.get();
    }   

// 最后调用了Looper.loop()
    /**
     * Run the message queue in this thread. Be sure to call
     * {@link #quit()} to end the loop.
     */
    public static void loop() {
        // Looper.loop()会进入一个死循环，但是这个循环并不会导致卡死，
        // 涉及到Linux pipe/epoll机制，简单说就是在主线程的MessageQueue没有消息时，
        // 便阻塞在loop的queue.next()中的nativePollOnce()方法里，此时主线程会释放CPU资源进入休眠状态，
        // 直到下个消息到达或者有事务发生，通过往pipe管道写端写入数据来唤醒主线程工作。
        // 这里采用的epoll机制，是一种IO多路复用机制，可以同时监控多个描述符，
        // 当某个描述符就绪(读或写就绪)，则立刻通知相应程序进行读或写操作，本质同步I/O，即读写是阻塞的。
        //  所以说，主线程大多数时候都是处于休眠状态，并不会消耗大量CPU资源。
        // 先拿到当前线程的Looper，然后拿到Looper中的MessageQueue
        final Looper me = myLooper();
        if (me == null) {
            throw new RuntimeException("No Looper; Looper.prepare() wasn't called on this thread.");
        }
        final MessageQueue queue = me.mQueue;

        // ...
        // 开启循环，Android中主线程上所有的点击事件、UI绘制都是通过Message发送到MessageQueue中等待执行
        // 所以这里必须是死循环，因为如果跳出了这个循环说明已经无法再继续处理任何Message，那么随之而来的肯定就是
        // 应用崩溃或者重启Looper，但是这里的循环并不会导致卡死，理由在上面已经简要说明了
        for (;;) {
            // 循环的作用就是通过queue.next()不断地从MessageQueue取出Message，next方法中也是一个死循环，
            // 正常情况下queue.next()应该返回一个有效的Message，或者休眠不返回任何值，如果返回null，
            // 说明出了问题
            Message msg = queue.next(); // might block
            if (msg == null) {
                // 当取出的message为空时说明MessageQueue被终止了，因此跳出循环，执行其他操作，比如重启Looper或者崩溃？
                // No message indicates that the message queue is quitting.
                return;
            }

            // ...
            // 当我们取到有效的Message后，就需要知道这个Message应该由谁来处理，即Target，从Message源码中可知，
            // 这个Target实际上就是Handler，最终调用的就是Handler的dispatchMessage方法，从这里我们就知道了
            // 只要其他线程能够将Message发送到主线程的MessageQueue中，那么这个Message就可以被主线程的Handler处理
            try {
                msg.target.dispatchMessage(msg);
                dispatchEnd = needEndTime ? SystemClock.uptimeMillis() : 0;
            } finally {
                if (traceTag != 0) {
                    Trace.traceEnd(traceTag);
                }
            }

            // ...
            // 最后需要对Message对象进行回收
            msg.recycleUnchecked();
        }
    }
```

ActivityThread的main方法中对主线程的Looper进行初始化，同样的主线程的MessageQueue也准备好对其中的Message进行分发，这都是通过死循环实现的，相当于MessageQueue是一个等待队列，有消息来了，他就取消息并调用Message对应的Handler的dispatchMessage方法，如果没有就休眠，然后我们看看Handler的初始化以及Message的发送是如何实现的

```java
// Handler.java Handler的构造方法分为两类，一类是参数带Looper的，另一类是不带Looper
// 不带Looper的构造函数最终会调用到最后一个构造函数，并进行Looper的初始化；
// 带Looper的构造函数会直接保存参数中的Looper实例
    public Handler() {
        this(null, false);
    }

    public Handler(Callback callback) {
        this(callback, false);
    }

    public Handler(Looper looper) {
        this(looper, null, false);
    }

    public Handler(Looper looper, Callback callback) {
        this(looper, callback, false);
    }

    public Handler(boolean async) {
        this(null, async);
    }

    public Handler(Looper looper, Callback callback, boolean async) {
        mLooper = looper;
        mQueue = looper.mQueue;
        mCallback = callback;
        mAsynchronous = async;
    }

    public Handler(Callback callback, boolean async) {
        if (FIND_POTENTIAL_LEAKS) {
            final Class<? extends Handler> klass = getClass();
            if ((klass.isAnonymousClass() || klass.isMemberClass() || klass.isLocalClass()) &&
                    (klass.getModifiers() & Modifier.STATIC) == 0) {
                Log.w(TAG, "The following Handler class should be static or leaks might occur: " +
                    klass.getCanonicalName());
            }
        }
        // Looper的myLooper方法会初始化当前线程的Looper
        mLooper = Looper.myLooper();
        if (mLooper == null) {
            throw new RuntimeException(
                "Can't create handler inside thread " + Thread.currentThread()
                        + " that has not called Looper.prepare()");
        }
        mQueue = mLooper.mQueue;
        mCallback = callback;
        mAsynchronous = async;
    }
```

然后调用`handler.sendMessage(message);`

```java
// Handler.java sendMessage方法会直接调用sendMessageDelayed
// sendMessageDelayed就是多个延时的效果
    public final boolean sendMessage(Message msg)
    {
        return sendMessageDelayed(msg, 0);
    }

    public final boolean sendMessageDelayed(Message msg, long delayMillis)
    {
        if (delayMillis < 0) {
            delayMillis = 0;
        }
        // 通过加上SystemClock.uptimeMillis()可以直接得到执行的具体时间
        return sendMessageAtTime(msg, SystemClock.uptimeMillis() + delayMillis);
    }

    public boolean sendMessageAtTime(Message msg, long uptimeMillis) {
        MessageQueue queue = mQueue;
        if (queue == null) {
            RuntimeException e = new RuntimeException(
                    this + " sendMessageAtTime() called with no mQueue");
            Log.w("Looper", e.getMessage(), e);
            return false;
        }
        // 最终还是使用Handler的MessageQueue
        return enqueueMessage(queue, msg, uptimeMillis);
    }

    private boolean enqueueMessage(MessageQueue queue, Message msg, long uptimeMillis) {
        // 注意这里将Message的target设置为当前handler
        msg.target = this;
        if (mAsynchronous) {
            msg.setAsynchronous(true);
        }
        // 然后调用MessageQueue的enqueueMessage方法
        return queue.enqueueMessage(msg, uptimeMillis);
    }

// MessageQueue.java enqueueMessage将Message加入链表中
    boolean enqueueMessage(Message msg, long when) {
        if (msg.target == null) {
            throw new IllegalArgumentException("Message must have a target.");
        }
        if (msg.isInUse()) {
            throw new IllegalStateException(msg + " This message is already in use.");
        }

        synchronized (this) {
            // 如果MessageQueue被终止了，那么Message还需要回收
            if (mQuitting) {
                IllegalStateException e = new IllegalStateException(
                        msg.target + " sending message to a Handler on a dead thread");
                Log.w(TAG, e.getMessage(), e);
                msg.recycle();
                return false;
            }

            msg.markInUse();
            msg.when = when;
            Message p = mMessages;
            boolean needWake;
            // 根据msg.next基本可以发现Message是一个链表中的节点，也就是说MessageQueue中的mMessages
            // 是一种链表形式的结构，其中mMessages是表头，当执行next方法时就会将表头也就是mMessages表示的
            // Message返回，当我们传入的Message满足以下任意条件时，可以将此Message作为表头：
            // 1. 表头本身为空，很明显当没有任何Message传入的时候；
            // 2. 当我们传入的Message没有任何延迟，这也很显然，立即执行的Message当然要放第一个；
            // 3. 当我们传入的Message的执行时间在表头的执行时间之前，这也很显然，按照时间排序。
            if (p == null || when == 0 || when < p.when) {
                // New head, wake up the event queue if blocked.
                msg.next = p;
                mMessages = msg;
                needWake = mBlocked;
            } else {
                // 如果Message不是表头位置，那么肯定就是链表中的某个位置
                // Inserted within the middle of the queue.  Usually we don't have to wake
                // up the event queue unless there is a barrier at the head of the queue
                // and the message is the earliest asynchronous message in the queue.
                needWake = mBlocked && p.target == null && msg.isAsynchronous();
                Message prev;
                for (;;) {
                    // 链表的遍历，还要判断时间when
                    prev = p;
                    p = p.next;
                    if (p == null || when < p.when) {
                        break;
                    }
                    if (needWake && p.isAsynchronous()) {
                        needWake = false;
                    }
                }
                // 这就很简单了，有序链表中加入某个节点，排序方式为when的值
                msg.next = p; // invariant: p == prev.next
                prev.next = msg;
            }

            // We can assume mPtr != 0 because mQuitting is false.
            if (needWake) {
                nativeWake(mPtr);
            }
        }
        return true;
    }
```

到这里我们就知道了Message被Handler加到了Handler线程的MessageQueue中，而Handler线程中的Looper一直在等待Message进入MessageQueue，通过queue.next()取出Message，然后调用Handler的dispatchMessage方法

```java
    /**
     * Handle system messages here.
     */
    public void dispatchMessage(Message msg) {
        // dispatchMessage处理Message的方式也很简单
        // 首先判断Message是否设置了Callback，如果有
        // 则执行message.callback.run()
        if (msg.callback != null) {
            handleCallback(msg);
        } else {
            // 如果没有，则判断Handler是否初始化设置了Callback，
            // 这个和Handler的构造函数相关
            if (mCallback != null) {
                if (mCallback.handleMessage(msg)) {
                    return;
                }
            }
            // 否则就执行handler重写的handleMessage方法，
            // 这个方法是在我们继承Handler时重写的，或者
            // 在使用Handler匿名内部类时重写的
            handleMessage(msg);
        }
    }
```

以上就是完整的通过Handler从子线程发送消息到主线程并执行的过程，也解决了我的一些问题：

> 1.为什么要设计Handler来传输消息？

因为多线程的情况下并不确定子线程何时能够执行完毕获取数据，所以需要设计Handler实现一种回调机制，即当子线程数据获取完成后将数据传到主线程中，通过主线程中的回调决定如何处理传来的数据。

> 2.为什么要用MessageQueue和Looper这种工具？

我想是因为既然子线程并不确定何时结束，干脆










## 2. AsyncTask


## 3. EventBus


## 4. RxJava








