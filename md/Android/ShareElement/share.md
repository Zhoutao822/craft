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
// 这里对应了上面说到的问题，Fragment1中的transitionName不重要，仅仅需要让它们的transitionName唯一即可，
// 否则会出现显示其他图片的异常
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

首先获取图片数据

```java
class Constants {

    static List<String> getImageUrls() {
        List<String> data = new ArrayList<>();
        data.add("https://i.loli.net/2020/01/02/ClMXcUkJNETpYHb.jpg");
        data.add("https://i.loli.net/2020/01/02/ulnhD8S79w4IfaY.jpg");
        data.add("https://i.loli.net/2020/01/02/i9IFevNYqKVRcXP.jpg");
        data.add("https://i.loli.net/2020/01/02/7QDskmZunBg4GEj.jpg");
        data.add("https://i.loli.net/2020/01/02/eHzuXSqIoUbh8Mc.jpg");
        data.add("https://i.loli.net/2020/01/02/biSqYO73CLvjh8p.jpg");
        data.add("https://i.loli.net/2020/01/02/a4NjuqfMmckoVT2.jpg");
        data.add("https://i.loli.net/2020/01/02/jSoFtq7VRBM6TUZ.jpg");
        data.add("https://i.loli.net/2020/01/02/nw3vUZBlyIph1oH.jpg");
        data.add("https://i.loli.net/2020/01/02/y3wGlkoXq4EWSDt.jpg");
        return data;
    }
}
```

然后定义RecyclerView相关代码

```java
public class MyAdapter extends RecyclerView.Adapter<MyAdapter.MyViewHolder> {

    private List<String> data;

    private Context context;

    public MyAdapter(List<String> data, Context context, OnItemClickListener onItemClickListener) {
        this.data = data;
        this.context = context;
        this.onItemClickListener = onItemClickListener;
    }

    @NonNull
    @Override
    public MyViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.layout_item, parent, false);
        return new MyViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull final MyViewHolder holder, final int position) {
        // 这里没有设置imageView和textView的transitionName也可以正常运行
        String url = data.get(position);
        holder.textView.setText(url);
        loadImage(url, holder);
        holder.imageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                onItemClickListener.onItemClick(holder, position);
            }
        });
    }

    // 分别通过Glide和Picasso加载图片
    private void loadImage(String url, MyViewHolder holder) {
        Glide.with(context)
                .load(url)
                .centerCrop()
                .into(holder.imageView);
//        Picasso.get()
//                .load(url)
//                .fit()
//                .centerCrop()
//                .into(holder.imageView);
    }

    @Override
    public int getItemCount() {
        return data.size();
    }

    class MyViewHolder extends RecyclerView.ViewHolder {

        public ImageView imageView;
        public TextView textView;

        public MyViewHolder(@NonNull View itemView) {
            super(itemView);
            imageView = itemView.findViewById(R.id.item_image);
            textView = itemView.findViewById(R.id.item_text);
        }
    }

    private OnItemClickListener onItemClickListener;

    public interface OnItemClickListener {
        void onItemClick(MyViewHolder viewHolder, int position);
    }
}
```

```xml
<!-- layout_item.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="150dp"
    android:layout_marginBottom="10dp"
    android:orientation="vertical">

    <ImageView
        android:id="@+id/item_image"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:layout_gravity="center"
        tools:src="@drawable/ic_launcher_foreground" />

    <TextView
        android:id="@+id/item_text"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:lines="1"
        android:textSize="16sp"
        tools:text="aaaaaa" />

</LinearLayout>
```

然后是Activity的代码

```java
// ThirdActivity.java
public class ThirdActivity extends AppCompatActivity implements MyAdapter.OnItemClickListener {

    private RecyclerView recyclerView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_third);

        MyAdapter adapter = new MyAdapter(Constants.getImageUrls(), this, this);
        recyclerView = findViewById(R.id.list);
        recyclerView.setLayoutManager(new GridLayoutManager(this, 2));
        recyclerView.setAdapter(adapter);
    }

    @Override
    public void onItemClick(MyAdapter.MyViewHolder viewHolder, int position) {
        Intent intent = new Intent(ThirdActivity.this, ForthActivity.class);
        intent.putExtra("position", position);
        // 与单个共享元素不同的是，多个共享元素动画需要使用Pair传参，而且需要强制转换类型为View
        Pair<View, String> imagePair = Pair.create((View)viewHolder.imageView, "image");
        Pair<View, String> textPair = Pair.create((View)viewHolder.textView, "text");
        ActivityOptionsCompat options = ActivityOptionsCompat.
                makeSceneTransitionAnimation(this, imagePair, textPair);
        startActivity(intent, options.toBundle());
    }
}

// ForthActivity.java
public class ForthActivity extends AppCompatActivity {

    private TextView textView;
    private ImageView imageView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_forth);
        int position = getIntent().getIntExtra("position", 0);
        textView = findViewById(R.id.text_detail);
        imageView = findViewById(R.id.image_detail);
        textView.setText(Constants.getImageUrls().get(position));
        loadImage(Constants.getImageUrls().get(position), imageView);
    }

    // 分别通过Glide和Picasso加载图片，注意这里与MyAdapter使用不同的框架也是没有问题的
    private void loadImage(String url, ImageView view) {
        // 关键代码supportPostponeEnterTransition()方法，可以使得Activity
        // 延迟显示，直到执行了supportStartPostponedEnterTransition()方法。
        // 也就是说，为了使图片能够先从网络上缓存下来再显示，可以在图片缓存成功的
        // 回调方法中调用supportStartPostponedEnterTransition()
        supportPostponeEnterTransition();

        Glide.with(this)
                .load(url)
                .centerCrop()
                .dontAnimate() // 实测这一行没有什么用
                .listener(new RequestListener<Drawable>() {
                    @Override
                    public boolean onLoadFailed(@Nullable GlideException e, Object model, Target<Drawable> target, boolean isFirstResource) {
                        supportStartPostponedEnterTransition();
                        return false;
                    }

                    @Override
                    public boolean onResourceReady(Drawable resource, Object model, Target<Drawable> target, DataSource dataSource, boolean isFirstResource) {
                        supportStartPostponedEnterTransition();
                        return false;
                    }
                })
                .into(view);


//        Picasso.get()
//                .load(url)
//                .noFade()  // 实测这一行没有什么用
//                .into(view, new Callback() {
//                    @Override
//                    public void onSuccess() {
//                        supportStartPostponedEnterTransition();
//                    }
//
//                    @Override
//                    public void onError(Exception e) {
//                        supportStartPostponedEnterTransition();
//                    }
//                });
    }
}
```

最终效果

{% asset_img share5.gif %}

这个显示效果有几个问题，一是TextView字体大小突变，二是图片返回时会有微小的大小反弹现象，三是图片如果卡在状态栏上会出现短时间覆盖状态栏的现象，最后是点击时不会立即跳转，会出现明显的卡顿。如果需要解决上述几个问题，可以参考[Github animation-samples](https://github.com/android/animation-samples)中的Unslpash示例。

{% asset_img share6.gif %}

可以发现这个示例没有出现上面我所发生的显示效果问题，如果仔细查看代码可以发现为了优化这个效果加入了一些的自定义动画以及自定义View。

## 3. 复杂效果的优化

具体可以参考[Github animation-samples](https://github.com/android/animation-samples)中的Unslpash示例。

Unslpash示例具体实现了一下几个细节效果：

1. 在图片详情页使用了ViewPager，可以左右滑动切换图片；
2. 当我们左右滑动切换图片再返回时，RecyclerView会滑动到对应的图片，而且有返回动画效果；
3. 点击查看图片详情时动画没有卡顿的感觉，而且字体大小有良好的变换动画效果，不是突变；
4. ViewPager左右滑动也没有产生加载的卡顿现象。

### 3.1 效果实现分析

首先是数据来源，Unslpash示例数据来自于`https://unsplash.it`，通过Retrofit获取，示例仅获取12张图片，构造的Photo数据结构就不用分析了，很简单。

然后是两个Activity的动画效果，是通过Theme设置的，分别对MainActivity和DetailActivity使用不同的Theme，即最主要的动画效果是通过xml定义的，java代码只控制逻辑

```xml
<!-- MainActivity -->
<style name="App.Home">
    <item name="android:windowExitTransition">@transition/grid_exit</item>
    <item name="android:windowReenterTransition">@transition/grid_reenter</item>
</style>

<!-- DetailActivity -->
<style name="App.Details">
    <item name="android:windowSharedElementEnterTransition">
        @transition/shared_main_detail
    </item>
</style>
```

MainActivity的非共享元素移出界面时的效果是grid_exit，即爆炸效果；返回MainActivity时是grid_reenter，即从上向下滑动效果；DetailActivity的共享元素进入界面的效果是shared_main_detail，分别定义了photo和text的动画效果，photo使用了传统的几个动画就不说了，text使用的是自定义的动画，这个TextResize类还是有点复杂，所以会用就行了，而且不会出现在java代码中。

```xml
<!-- grid_exit.xml -->
<explode />

<!-- grid_reenter.xml -->
<slide
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:slideEdge="top"
    android:duration="300"
    android:interpolator="@android:interpolator/linear_out_slow_in">
</slide>

<!-- shared_main_detail.xml -->
<transitionSet xmlns:android="http://schemas.android.com/apk/res/android">
    <transitionSet>
        <targets>
            <target android:targetId="@id/photo" />
        </targets>
        <changeBounds>
            <arcMotion android:maximumAngle="50"/>
        </changeBounds>
        <changeTransform />
        <changeClipBounds />
        <changeImageTransform />
    </transitionSet>
    <transitionSet>
        <targets>
            <target android:targetId="@id/author" />
        </targets>
        <transition class="com.example.android.unsplash.transition.TextResize" />
        <changeBounds />
    </transitionSet>
    <!-- recolor不知道有什么用，删了也没有区别 -->
    <recolor>
        <targets>
            <target android:targetId="@android:id/statusBarBackground" />
            <target android:targetId="@android:id/navigationBarBackground" />
        </targets>
    </recolor>
</transitionSet>
```

从MainActivity点击跳转到DetailActivity时需要通过Intent传入几个数据，比如当前界面中text的属性值，点击的图片索引以及从网络请求得到的图片url等等

```java
@NonNull
private static Intent getDetailActivityStartIntent(Activity host, ArrayList<Photo> photos,
                                                    int position, PhotoItemBinding binding) {
    final Intent intent = new Intent(host, DetailActivity.class);
    intent.setAction(Intent.ACTION_VIEW);
    intent.putParcelableArrayListExtra(IntentUtil.PHOTO, photos);
    intent.putExtra(IntentUtil.SELECTED_ITEM_POSITION, position);
    intent.putExtra(IntentUtil.FONT_SIZE, binding.author.getTextSize());
    intent.putExtra(IntentUtil.PADDING,
            new Rect(binding.author.getPaddingLeft(),
                    binding.author.getPaddingTop(),
                    binding.author.getPaddingRight(),
                    binding.author.getPaddingBottom()));
    intent.putExtra(IntentUtil.TEXT_COLOR, binding.author.getCurrentTextColor());
    return intent;
}
```

在DetailActivity中通过getIntent方法获取传入的数据，构造DetailSharedElementEnterCallback，通过setEnterSharedElementCallback设置回调；setEnterSharedElementCallback可以监听共享元素进入此Activity时的状态，由sharedElementCallback自定义

```java
@Override
protected void onCreate(Bundle savedInstanceState) {
    // ...
    Intent intent = getIntent();
    sharedElementCallback = new DetailSharedElementEnterCallback(intent);
    setEnterSharedElementCallback(sharedElementCallback);
    initialItem = intent.getIntExtra(IntentUtil.SELECTED_ITEM_POSITION, 0);
    setUpViewPager(intent.<Photo>getParcelableArrayListExtra(IntentUtil.PHOTO));
    // ...
}
```

DetailSharedElementEnterCallback的主要功能是在Activity切换时调整TextView的属性以及对共享元素进行绑定。从这个Callback可以看出来实际动画效果是发生在DetailActivity中，首先当处于onCreate方法中，在调用`super.onCreate(savedInstanceState);`之前设置DetailSharedElementEnterCallback，此时动画还未开始。

按照顺序执行`onMapSharedElements->onSharedElementStart->onSharedElementEnd`方法，在onMapSharedElements方法中需要将对应的共享元素View与其transitionName关联起来，这里的作用其实等价于在MainActivity中生成的Pair对象，试想一下如果我们在点击时绑定的是position为1的ImageView，而如果我们在ViewPager中滑动后position变为4，那么我们就需要更新Pair对象，否则返回时动画效果就不是返回position为4的ImageView。所以只能在Callback中处理，由于使用了Databinding而且两个Activity中的ImageView的transitionName相同，所以简单的添加即可，将其他不需要变换动画的元素移出Map也可以在这里操作。

然后在onSharedElementStart方法中会先将DetailActivity中的TextView的属性修改为MainActivity中对应TextView的属性，最后在onSharedElementEnd方法中将TextView设置为DetailActivity中原本的属性即可，也就是说从`onSharedElementStart->onSharedElementEnd`就是动画的过程了。

```java
public class DetailSharedElementEnterCallback extends SharedElementCallback {
// ...

    @Override
    public void onSharedElementStart(List<String> sharedElementNames,
                                     List<View> sharedElements,
                                     List<View> sharedElementSnapshots) {
        TextView author = getAuthor();
        targetTextSize = author.getTextSize();
        targetTextColors = author.getTextColors();
        targetPadding = new Rect(author.getPaddingLeft(),
                author.getPaddingTop(),
                author.getPaddingRight(),
                author.getPaddingBottom());
        if (IntentUtil.hasAll(intent,
                IntentUtil.TEXT_COLOR, IntentUtil.FONT_SIZE, IntentUtil.PADDING)) {
            author.setTextColor(intent.getIntExtra(IntentUtil.TEXT_COLOR, Color.BLACK));
            float textSize = intent.getFloatExtra(IntentUtil.FONT_SIZE, targetTextSize);
            author.setTextSize(TypedValue.COMPLEX_UNIT_PX, textSize);
            Rect padding = intent.getParcelableExtra(IntentUtil.PADDING);
            author.setPadding(padding.left, padding.top, padding.right, padding.bottom);
        }
    }

    @Override
    public void onSharedElementEnd(List<String> sharedElementNames,
                                   List<View> sharedElements,
                                   List<View> sharedElementSnapshots) {
        TextView author = getAuthor();
        author.setTextSize(TypedValue.COMPLEX_UNIT_PX, targetTextSize);
        if (targetTextColors != null) {
            author.setTextColor(targetTextColors);
        }
        if (targetPadding != null) {
            author.setPadding(targetPadding.left, targetPadding.top,
                    targetPadding.right, targetPadding.bottom);
        }
        if (currentDetailBinding != null) {
            forceSharedElementLayout(currentDetailBinding.description);
        }
    }    

    @Override
    public void onMapSharedElements(List<String> names, Map<String, View> sharedElements) {
        removeObsoleteElements(names, sharedElements, mapObsoleteElements(names));
        mapSharedElement(names, sharedElements, getAuthor());
        mapSharedElement(names, sharedElements, getPhoto());
    }

    public void setBinding(@NonNull DetailViewBinding binding) {
        currentDetailBinding = binding;
        currentPhotoBinding = null;
    }

    public void setBinding(@NonNull PhotoItemBinding binding) {
        currentPhotoBinding = binding;
        currentDetailBinding = null;
    }

    private TextView getAuthor() {
        if (currentPhotoBinding != null) {
            return currentPhotoBinding.author;
        } else if (currentDetailBinding != null) {
            return currentDetailBinding.author;
        } else {
            throw new NullPointerException("Must set a binding before transitioning.");
        }
    }

    private ImageView getPhoto() {
        if (currentPhotoBinding != null) {
            return currentPhotoBinding.photo;
        } else if (currentDetailBinding != null) {
            return currentDetailBinding.photo;
        } else {
            throw new NullPointerException("Must set a binding before transitioning.");
        }
    }

    /**
     * Maps all views that don't start with "android" namespace.
     *
     * @param names All shared element names.
     * @return The obsolete shared element names.
     */
    @NonNull
    private List<String> mapObsoleteElements(List<String> names) {
        List<String> elementsToRemove = new ArrayList<>(names.size());
        for (String name : names) {
            if (name.startsWith("android")) continue;
            elementsToRemove.add(name);
        }
        return elementsToRemove;
    }

    /**
     * Removes obsolete elements from names and shared elements.
     *
     * @param names            Shared element names.
     * @param sharedElements   Shared elements.
     * @param elementsToRemove The elements that should be removed.
     */
    private void removeObsoleteElements(List<String> names,
                                        Map<String, View> sharedElements,
                                        List<String> elementsToRemove) {
        if (elementsToRemove.size() > 0) {
            names.removeAll(elementsToRemove);
            for (String elementToRemove : elementsToRemove) {
                sharedElements.remove(elementToRemove);
            }
        }
    }

    /**
     * Puts a shared element to transitions and names.
     *
     * @param names          The names for this transition.
     * @param sharedElements The elements for this transition.
     * @param view           The view to add.
     */
    private void mapSharedElement(List<String> names, Map<String, View> sharedElements, View view) {
        String transitionName = view.getTransitionName();
        names.add(transitionName);
        sharedElements.put(transitionName, view);
    }    

    private void forceSharedElementLayout(View view) {
        int widthSpec = View.MeasureSpec.makeMeasureSpec(view.getWidth(),
                View.MeasureSpec.EXACTLY);
        int heightSpec = View.MeasureSpec.makeMeasureSpec(view.getHeight(),
                View.MeasureSpec.EXACTLY);
        view.measure(widthSpec, heightSpec);
        view.layout(view.getLeft(), view.getTop(), view.getRight(), view.getBottom());
    }
}
```

以上就是从MainActivity点击跳转到DetailActivity的全部流程，当然Unsplash示例还有ViewPager以及返回动画效果。

当我们左右滑动时会调用DetailViewPagerAdapter的setPrimaryItem，在这个方法中我们设置的上面Callback的View binding，将其置为当前的ImageView，此时如果点击返回键，那么Callback的执行顺序是`onMapSharedElements->onMapSharedElements->onSharedElementEnd->onSharedElementStart->onSharedElementStart->onSharedElementEnd`，这里分为两个阶段，因为此时在两个Activity中都有Callback，第一个onMapSharedElements是DetailActivity的，这里重新绑定position为4的ImageView；第二个onMapSharedElements是MainActivity的的，在onActivityReenter方法（Activity返回）中执行，此时MainActivity已经知道了当前position为4，因此滑动RecyclerView到position为4的位置，并且将其对应的binding传入MainActivity的Callback中；然后是`onSharedElementEnd->onSharedElementStart`，这个状态是DetailActivity的动作，很显然这个效果就是上面动画的逆过程，






### 3.2 尝试在Fragment中实现类似效果


## 4. 使用技巧总结

1. Fragment中使用时，当前Fragment的共享元素的`transitionName`必须存在但是与目的地Fragment不同也能用，且RecyclerView中的每一个共享元素都必须设置为不同的`transitionName`（Activity中当前Activity的`transitionName`可以不设置，包括使用了RecyclerView，目的地Activity必须设置），**但是实际使用时请务必将对应共享元素的`transitionName`设置为相同（RecyclerView除外）**；
2. Fragment中使用时，当目的地Fragment中共享元素被嵌套了多层，则可能出现滑动动画缺失现象，可以通过`marginTop:1dp`解决；Activity中不会有这种现象；
3. 切换动画产生时会导致状态栏、ActionBar以及Toolbar的闪烁，可以通过在动画中将这些View的id排除即可避免；
4. 如果使用了Glide或者Picasso等图片加载框架从网络请求加载图片，可以在Activity中设置`supportPostponeEnterTransition()`以及`supportStartPostponedEnterTransition()`方法来确保图片能够先缓存再显示（Fragment中是`postponeEnterTransition()`和`startPostponedEnterTransition()`），但是会导致另一个问题，点击跳转非常卡顿；
5. ViewPager配合使用实现左右滑动查看图片时，返回动画会出错，显示错误的图片，此时可以通过对ViewPager中的Fragment设置`setSharedElementReturnTransition(null)`来禁用返回动画（[参考](https://mikescamell.com/shared-element-transitions-part-4-recyclerview/)）。





