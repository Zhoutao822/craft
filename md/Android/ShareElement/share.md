# 共享元素动画效果

参考：

> [Android Developers文档指南](https://developer.android.com/training/transitions/start-activity)
> [Github animation-samples](https://github.com/android/animation-samples)
> [Shared Element Transitions - Part 1: Activities](https://mikescamell.com/shared-element-transitions-part-1/)
> [Shared Element Transitions - Part 2: Fragments](https://mikescamell.com/shared-element-transitions-part-2/)
> [android_guides](https://github.com/codepath/android_guides/wiki/Shared-Element-Activity-Transition)
> [Fragment transitions with shared elements](https://medium.com/@bherbst/fragment-transitions-with-shared-elements-7c7d71d31cbb)

共享元素可以在Activity之间或者Fragment之间实现非常舒适的动画效果，如下图所示，特别是在跳转的界面之间拥有相同的界面元素，比如同一张图片但是大小不同，同一个View但是位置不同。需要注意的是最低api需要为21，即Android LOLLIPOP。

{% asset_img cat.gif %}

## 1. Fragment之间共享元素

首先实现在Fragment之间的共享元素动画，因为Fragment可能比Activity更加常用，这两者实现的代码略有区别，而且在我的测试过程中还发现了部分奇怪的问题。

### 1.1 简单使用

首先创建两个Fragment，定义各自布局，关键是两个布局中需要共享的元素需要指定一个属性`android:transitionName`，可以是任何自定义的字符串。

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
                    // 共享元素的动画效果，必须在目的地Fragment调用，否则无效，系统提供了一些动画效果，
                    // 比如move、fade等等，可以直接使用，也可以通过继承TransitionSet实现自定义动画效果
                    destination.setSharedElementEnterTransition(TransitionInflater.from(getContext()).inflateTransition(android.R.transition.move));
                    destination.setSharedElementReturnTransition(TransitionInflater.from(getContext()).inflateTransition(android.R.transition.move));

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
                            // 对象以及它的transitionName，可以通过ViewCompat.getTransitionName方法获取，
                            // 也可以写死
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

对应的两个布局文件，两者的区别仅仅是layout1中TextView有上边距，`android:transitionName="textView"`相同

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

具体可以参考[FragmentTransitionSample](https://github.com/bherbst/FragmentTransitionSample)，其中还包括自定义TransitionSet的实现。

## 2. Activity之间共享元素

从Fragment提供的方法可知，Fragment之间共享元素仅能实现一个View的动画，如果在一个界面中需要对多个View实现动画就只能在Activity中实现了。






