# 共享元素动画效果

参考：

> [Android Developers文档指南](https://developer.android.com/training/transitions/start-activity)
> [Github animation-samples](https://github.com/android/animation-samples)
> [Shared Element Transitions - Part 1: Activities](https://mikescamell.com/shared-element-transitions-part-1/)
> [Shared Element Transitions - Part 2: Fragments](https://mikescamell.com/shared-element-transitions-part-2/)
> [Shared Element Transitions - Part 3: Picasso & Glide](https://mikescamell.com/shared-element-transitions-part-3/)
> [android_guides](https://github.com/codepath/android_guides/wiki/Shared-Element-Activity-Transition)
> [Fragment transitions with shared elements](https://medium.com/@bherbst/fragment-transitions-with-shared-elements-7c7d71d31cbb)

共享元素可以在Activity之间或者Fragment之间实现非常舒适的动画效果，如下图所示，特别是在跳转的界面之间拥有相同的界面元素，比如同一张图片但是大小不同，同一个View但是位置不同。需要注意的是最低api需要为21，即Android LOLLIPOP。

{% asset_img cat.gif %}

## 1. Fragment之间共享元素

首先实现在Fragment之间的共享元素动画，因为Fragment可能比Activity更加常用，这两者实现的代码略有区别，而且在我的测试过程中还发现了部分奇怪的问题。

### 1.1 简单使用

首先创建两个Fragment，定义各自布局，关键是两个布局中需要共享的元素需要指定一个属性`android:transitionName`，可以是任何自定义的字符串，其中Fragment1中的共享元素的`transitionName`可以与Fragment2中的共享元素不同，但是必须要设置（通过xml或者`setTransitionName`方法），否则会报错。

```java
// Fragment1.java
public class Fragment1 extends Fragment {
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";
    private static final String TAG = Fragment1.class.getSimpleName();

    private TextView textView;

    // Fragment默认生成的实例化方法，参数这里没有用到，无所谓
    public static Fragment1 newInstance(String param1, String param2) {
        Fragment1 fragment = new Fragment1();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, param1);
        args.putString(ARG_PARAM2, param2);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        // 我们仅在Fragment中显示一个TextView
        textView = view.findViewById(R.id.textView1);
        textView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // 点击跳转到Fragment2，同理参数不重要
                Fragment2 destination = Fragment2.newInstance("1", "2");
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    // 定义共享元素的动画效果
                    // setSharedElementEnterTransition以及setSharedElementReturnTransition分别设置
                    // 共享元素的动画效果，在目的地Fragment调用Enter方法，当前Fragment调用Return方法，否则
                    // 无效，系统提供了一些动画效果，比如move、fade等等，可以直接使用，也可以通过继承
                    // TransitionSet实现自定义动画效果
                    destination.setSharedElementEnterTransition(TransitionInflater.from(getContext()).inflateTransition(android.R.transition.move));
                    setSharedElementReturnTransition(TransitionInflater.from(getContext()).inflateTransition(android.R.transition.move));

                    // setEnterTransition和setExitTransition设置除了共享元素之外其他View的动画效果
                    // 一般来说仅需要设置目的地Fragment的Enter效果和当前Fragment的Exit效果，同样系统
                    // 也提供比如Fade之类的效果
                    destination.setEnterTransition(new Fade());
                    setExitTransition(new Fade());
                }
                if (getFragmentManager() != null) {
                    getFragmentManager()
                            .beginTransaction()
                            // 在切换Fragment时调用addSharedElement方法，标记我们的共享元素，参数为共享元素
                            // 对象以及Fragment2中的共享元素的transitionName，可以写死，需要注意的是，这里传入
                            // 的transitionName需要与Fragment2中的共享元素相同。以我们的代码为例，只有在两个布
                            // 局中共享元素transitionName相同时才可以使用ViewCompat.getTransitionName方法获取
                            .addSharedElement(textView, Objects.requireNonNull(ViewCompat.getTransitionName(textView)))
                            .addToBackStack(TAG)
                            .replace(R.id.container, destination)
                            .commit();
                }
            }
        });
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.layout1, container, false);
    }
}

// Fragment2.java Fragment2没有加入任何效果，仅显示我们需要的布局
public class Fragment2 extends Fragment {
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";

    public static Fragment2 newInstance(String param1, String param2) {
        Fragment2 fragment = new Fragment2();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, param1);
        args.putString(ARG_PARAM2, param2);
        fragment.setArguments(args);
        return fragment;
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.layout2, container, false);
    }
}

```

对应的两个布局文件，两者的区别仅仅是layout1中TextView有上边距，`android:transitionName="textView"`相同（可以不同，因为Fragment1中的transitionName并不重要）

```xml
<!-- layout1.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal">

    <TextView
        android:id="@+id/textView1"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="200dp"
        android:text="qqqqqqqqqqqq"
        android:textSize="24sp"
        android:transitionName="textView" />

</LinearLayout>

<!-- layout2.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal">

    <TextView
        android:id="@+id/textView2"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="qqqqqqqqqqqq"
        android:textSize="24sp"
        android:transitionName="textView" />

</LinearLayout>
```

效果如下

{% asset_img share1.gif %}

当然我们实际应用中不会使用如此简单的布局，此时我仅仅修改layout2，增加一个ImageView，那么就会出现一个奇怪的Bug现象

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal">

        <ImageView
            android:layout_width="40dp"
            android:layout_height="40dp"
            android:background="@color/colorPrimary"
            android:src="@drawable/ic_launcher_foreground" />

        <TextView
            android:id="@+id/textView2"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="qqqqqqqqqqqq"
            android:textSize="24sp"
            android:transitionName="textView" />

    </LinearLayout>

</LinearLayout>
```

如下图所示，从Fragment1跳转到Fragment2时，TextView并没有按照轨迹移动，而实突然出现在顶部，但是返回时TextView按照轨迹移动，而我仅仅只是增加了一点布局。

{% asset_img share2.gif %}

更加奇怪的是如果上述布局layout2中，设置第二层LinearLayout的`android:layout_marginTop="1dp"`，那么又可以正常按照轨迹移动了，这里就不截图了。也就是说如果在实际应用过程中出现这样的显示效果问题，可以通过设置`layout_marginTop`来避免，但是可能会有1dp的显示问题。

### 1.2 RecyclerView以及图片缩放效果

具体可以参考[FragmentTransitionSample](https://github.com/bherbst/FragmentTransitionSample)，其中还包括自定义TransitionSet的实现。需要注意的是，在RecyclerView中添加`transitionName`的方式

```java
// 这里对应了上面说到的问题，Fragment1中的transitionName不重要，仅仅需要让它们的transitionName唯一即可
ViewCompat.setTransitionName(viewHolder.image, position + "_image");

getActivity().getSupportFragmentManager()
        .beginTransaction()
        // 只要最终addSharedElement方法添加的transitionName与Fragment2相同即可
        .addSharedElement(holder.image, "kittenImage")
        .replace(R.id.container, kittenDetails)
        .addToBackStack(null)
        .commit();
```

## 2. Activity之间共享元素

从Fragment提供的方法可知，Fragment之间共享元素仅能实现一个View的动画，如果在一个界面中需要对多个View实现动画就只能在Activity中实现了。

### 2.1 简单使用

首先看看之前在Fragment中存在的问题是否会同样出现在Activity中。与Fragment不同的是，在Activity中启用共享元素需要提前配置一下Theme

```xml
<style name="AppTheme" parent="Theme.AppCompat.Light.NoActionBar">
    <!-- Customize your theme here. -->
    <item name="colorPrimary">@color/colorPrimary</item>
    <item name="colorPrimaryDark">@color/colorPrimaryDark</item>
    <item name="colorAccent">@color/colorAccent</item>

    <!-- windowContentTransitions也可以通过getWindow().requestFeature(Window.FEATURE_CONTENT_TRANSITIONS)动态控制 -->
    <item name="android:windowContentTransitions">true</item>

    <!-- 也可以通过getWindow().setExitTransition(new Fade())动态控制 -->
    <!-- specify enter and exit transitions -->
    <item name="android:windowEnterTransition">@android:transition/fade</item>
    <item name="android:windowExitTransition">@android:transition/fade</item>

    <!-- 也可以通过getWindow().setSharedElementEnterTransition()动态控制 -->
    <!-- specify shared element transitions -->
    <item name="android:windowSharedElementEnterTransition">
        @android:transition/move
    </item>
    <item name="android:windowSharedElementExitTransition">
        @android:transition/move
    </item>

</style>
```

在Theme中控制和通过代码动态控制的区别是Theme是全局的设置，后续如果在代码中没有显示控制则会使用Theme的效果，动态控制的话可以对不同Activity设置不同的动画效果。

```java
// FirstActivity.java
public class FirstActivity extends AppCompatActivity {

    private TextView textView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_first);
        textView = findViewById(R.id.text_1);
        textView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(FirstActivity.this, SecondActivity.class);
                // 由于Activity是通过startActivity启动，所以使用makeSceneTransitionAnimation
                // 同理，这里的transitionName为"text"，与SecondActivity相同，而且这里并没有设置
                // FirstActivity的transitionName
                ActivityOptionsCompat options = ActivityOptionsCompat.
                        makeSceneTransitionAnimation(FirstActivity.this,
                                textView,
                                "text");
                startActivity(intent, options.toBundle());
            }
        });
    }
}

// SecondActivity.java
public class SecondActivity extends AppCompatActivity {

    private TextView textView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_second);
        textView = findViewById(R.id.text_2);
        // 动态设置transitionName
        ViewCompat.setTransitionName(textView, "text");
    }
}
```

而且Fragmen中存在的动画效果异常的问题没有出现在Activity中

```xml
<!-- activity_first.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal">

<!--    <LinearLayout-->
<!--        android:layout_width="match_parent"-->
<!--        android:layout_height="wrap_content">-->

        <TextView
            android:id="@+id/text_1"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="200dp"
            android:text="aaaaaaaaaaaaaa"
            android:textSize="24sp" />
<!--    </LinearLayout>-->

</LinearLayout>

<!-- activity_second.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal">

        <ImageView
            android:layout_width="40dp"
            android:layout_height="40dp"
            android:background="@color/colorPrimary"
            android:src="@drawable/ic_launcher_foreground" />

        <TextView
            android:id="@+id/text_2"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="aaaaaaaaaaaaaa"
            android:textSize="24sp" />

    </LinearLayout>

</LinearLayout>
```

具体效果如下，但是仔细观察可以发现存在问题，状态栏在动画过程中会闪烁

{% asset_img share3.gif %}

解决方法是指定状态栏或者其他控件不参加动画，原理是因为在动画过程中实际是通过一层windows ViewOverlay播放动画，这一层在包括了界面所有的View（状态栏也在其中），当我们指定动画时可以将状态栏的id排除出去就可以实现状态栏不参与动画，也就不会有闪烁的现象。

* Theme控制

```xml
// styles.xml
<!-- specify enter and exit transitions -->
<!-- 自定义fade.xml -->
<item name="android:windowEnterTransition">@transition/fade</item>
<item name="android:windowExitTransition">@transition/fade</item>

// fade.xml
<?xml version="1.0" encoding="utf-8"?>
<transitionSet xmlns:android="http://schemas.android.com/apk/res/android">
    <fade xmlns:android="http://schemas.android.com/apk/res/android">
        <targets>
            <!-- 可以设置statusBarBackground的id，也可以是我们自定义的控件的id，比如Toolbar -->
            <target android:excludeId="@android:id/statusBarBackground" />
            <target android:excludeId="@android:id/navigationBarBackground" />
<!--            <target android:excludeId="@id/appBar" />-->
        </targets>
    </fade>
</transitionSet>
```

* 动态代码控制

```java
// 当前Activity设置Exit效果，目的地Activity设置Enter效果
// FirstActivity.java
Fade fade = new Fade();
fade.excludeTarget(android.R.id.statusBarBackground, true);
fade.excludeTarget(android.R.id.navigationBarBackground, true);

getWindow().setExitTransition(fade);

// SecondActivity.java
Fade fade = new Fade();
fade.excludeTarget(android.R.id.statusBarBackground, true);
fade.excludeTarget(android.R.id.navigationBarBackground, true);

getWindow().setEnterTransition(fade);
```

* Activity设置独立Theme

```xml
// styles.xml
<style name="DefaultActivity" parent="AppTheme">
    <item name="android:windowEnterTransition">@transition/fade</item>
    <item name="android:windowExitTransition">@transition/fade</item>
</style>

// AndroidManifest.xml
<activity
    android:name=".SecondActivity"
    android:theme="@style/DefaultActivity" />
<activity
    android:name=".FirstActivity"
    android:theme="@style/DefaultActivity" />
```

{% asset_img share4.gif %}


### 2.2 RecyclerView复杂效果

上面写的代码都是用的本地图片，如果从网络中加载图片并在不同Activity中跳转，那么必然需要考虑在两个Activity中加载图片时的缓存时间，常用的图片加载框架有Picasso和Glide，可以参考上面给出的[链接](https://mikescamell.com/shared-element-transitions-part-4-recyclerview/)。



