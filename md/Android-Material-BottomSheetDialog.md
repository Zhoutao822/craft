参考：

[Material Design](https://material.io/develop/android/components/bottom-sheet-behavior/)

[Getting started with Material Components for Android](https://github.com/material-components/material-components-android/blob/master/docs/getting-started.md)

BottomSheetDialog，顾名思义就是从界面底部往上出现的Dialog，它是Material Design的控件之一，目前在[Material Components](https://github.com/material-components/material-components-android)库中。

{% asset_img bottomsheet-1.gif %}

<!-- more -->

## 1. 准备工作

Google推出的[Material Components](https://github.com/material-components/material-components-android)库包括了很多常用的控件，我们只需要直接用这些控件就可以实现很多复杂的功能或界面，但是在使用之前还需要一些准备工作，大致在[Getting started with Material Components for Android](https://github.com/material-components/material-components-android/blob/master/docs/getting-started.md)也给出了，我这里简要描述一下：

* 首先使是依赖（建议更新项目到androidx再继续），需要在`build.gradle`中加入Google's Maven Repository `google()`，然后加入库；

```gradle
  allprojects {
    repositories {
      google()
      jcenter()
    }
  }
```

```gradle
dependencies {
    // ...
    // 目前最新版为1.1.0-alpha07，有部分控件还是存在Bug
    implementation 'com.google.android.material:material:1.1.0-alpha07'
    // ...
  }
```

* 其次是`compileSdkVersion`需要在`28`或以上才能使用Material控件；
* 然后需要使用或继承`AppCompatActivity`，`AppCompatActivity`是专门为Material控件设计的Activity，如果不能继承则需要使用`AppCompatDelegate`；
* 最后是需要修改`AppTheme`，在`AndroidManifest.xml`里面修改主题，需要继承自Material Components themes，具体有哪些可以看上面给的地址，如果暂时不允许修改`AppTheme`，可以使用Material Components Bridge themes，这里的区别在于使用Material Components themes可能会导致你原来的应用中某些布局颜色UI发生改变，这时候需要重新修改一些资源文件；如果使用Bridge themes则不会修改原来应用的布局颜色UI等，却可以使用Material组件。

```xml
    <style name="AppTheme" parent="Theme.MaterialComponents.NoActionBar.Bridge">
        <!-- Customize your theme here. -->
        <item name="colorPrimary">@color/colorPrimary</item>
        <item name="colorPrimaryDark">@color/colorPrimaryDark</item>
        <item name="colorAccent">@color/colorAccent</item>
    </style>
```

到这里，准备工作基本完成，可以进行下一步使用Material组件了。

## 2. BottomSheetDialog使用

根据官网说明，BottomSheetDialog有两种使用方式（这里很多博客没有说明就直接给代码了），一种是Persistent，另一种是Modal，简而言之就是前者是固定的BottomSheetDialog，后者是动态调用的。

### Persistent BottomSheetDialog

设想一个使用场景，某个界面必定包含BottomSheetDialog，需要靠它实现其他功能的选择，举个例子，知乎的评论就是依靠BottomSheetDialog来实现的（一个东西看起来像鸭子，吃起来也像鸭子，那么它就是鸭子），而且有很明显的特征：在回答界面必定存在这个评论功能，那么我们可以将它视为Persistent固定场景，此时实现BottomSheetDialog的方式是使用BottomSheetBehavior，而不是`new BottomSheetDialog()`，实例代码如下：

* 首先是activity的布局文件`activity_second.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- 注意要使用BottomSheetBehavior，则必须使用CoordinatorLayout作为父布局，而且需要xmlns:app -->
<androidx.coordinatorlayout.widget.CoordinatorLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical">

        <Button
            android:id="@+id/btn_show"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="center"
            android:text="Show" />

    </LinearLayout>

    <!-- BottomSheetBehavior需要一个寄主，可以是LinearLayout也可以是其他，这个layout就是弹出的dialog布局，
     同时需要几个属性：
     app:behavior_hideable="true"否则BottomSheetDialog不会收起来
     app:behavior_peekHeight="300dp"设置BottomSheetDialog在STATE_COLLAPSED状态的高度，也可以不设置，这个会产生一种弹性收缩的效果，具体自行尝试
     app:elevation="6dp"设置z轴高度，可以产生一种悬浮效果，可以不设置
     app:layout_behavior="com.google.android.material.bottomsheet.BottomSheetBehavior"最重要的属性，简而言之就是让LinearLayout
     的行为变成BottomSheetDialog的行为，这样我们就不需要实例化一个BottomSheetDialog，取而代之的是通过BottomSheetBehavior来实现，
     需要注意的地方是，app:layout_behavior只能在CoordinatorLayout下直接子控件中使用，像这里的CoordinatorLayout->LinearLayout就可以
      -->
    <LinearLayout
        android:id="@+id/bottom_sheet"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:background="@color/white"
        android:orientation="vertical"
        app:behavior_hideable="true"
        app:behavior_peekHeight="300dp"
        app:elevation="6dp"
        app:layout_behavior="com.google.android.material.bottomsheet.BottomSheetBehavior">

        <!-- 这里随便加了几个子项，在BottomSheetBehavior布局下的子控件都是BottomSheetDialog一部分 -->

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal">

            <ImageView
                style="@style/MenuIcon"
                android:src="@drawable/ic_share_black_24dp" />

            <TextView
                style="@style/MenuText"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Share" />
        </LinearLayout>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal">

            <ImageView
                style="@style/MenuIcon"
                android:src="@drawable/ic_cloud_upload_black_24dp" />

            <TextView
                style="@style/MenuText"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Upload" />
        </LinearLayout>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal">

            <ImageView
                style="@style/MenuIcon"
                android:src="@drawable/ic_content_copy_black_24dp" />

            <TextView
                style="@style/MenuText"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Copy" />

        </LinearLayout>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal">

            <ImageView
                style="@style/MenuIcon"
                android:src="@drawable/ic_print_black_24dp" />

            <TextView
                style="@style/MenuText"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Print" />

        </LinearLayout>

    </LinearLayout>

</androidx.coordinatorlayout.widget.CoordinatorLayout>
```

这里用了`styles.xml`减少重复代码

```xml
    <style name="MenuIcon">
        <item name="android:layout_height">30dp</item>
        <item name="android:layout_width">30dp</item>
        <item name="android:layout_margin">15dp</item>
    </style>

    <style name="MenuText">
        <item name="android:layout_gravity">center_vertical</item>
        <item name="android:layout_marginStart">30dp</item>
        <item name="android:gravity">start</item>
        <item name="android:textColor">#00574B</item>
        <item name="android:textSize">20sp</item>
    </style>
```

* 然后是activity的代码`SecondActivity.java`

```java
public class SecondActivity extends AppCompatActivity {

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_second);
        // BottomSheetBehavior一共有5个状态：STATE_COLLAPSED/STATE_EXPANDED/STATE_DRAGGING/STATE_SETTLING/STATE_HIDDEN
        // 当你的布局文件中BottomSheetBehavior控件高度大于设置behavior_peekHeight，则Dialog会产生三种位置，一个是隐藏STATE_HIDDEN，
        // 另一个是STATE_EXPANDED即BottomSheetBehavior控件全部显示出来的位置，还有一个是介于前两者之间的STATE_COLLAPSED状态，
        // 此时露出来的Dialog高度为behavior_peekHeight；
        // 另一种情况是behavior_peekHeight大于BottomSheetBehavior控件高度，那么会产生一种弹性收缩的效果
        BottomSheetBehavior bottomSheetBehavior = BottomSheetBehavior.from(findViewById(R.id.bottom_sheet));
        bottomSheetBehavior.setState(BottomSheetBehavior.STATE_HIDDEN);

        findViewById(R.id.btn_show).setOnClickListener(v -> {
            // 这里通过判断当前状态来进行收缩和打开，与此同时Dialog支持直接滑动关闭
            if (bottomSheetBehavior.getState() == BottomSheetBehavior.STATE_HIDDEN) {
                bottomSheetBehavior.setState(BottomSheetBehavior.STATE_COLLAPSED);
            } else if (bottomSheetBehavior.getState() == BottomSheetBehavior.STATE_COLLAPSED) {
                bottomSheetBehavior.setState(BottomSheetBehavior.STATE_HIDDEN);
            }
        });
        // 通过设置BottomSheetCallback来控制状态变化产生的其他效果，也可以控制滑动过程中产生其他效果
        bottomSheetBehavior.setBottomSheetCallback(new BottomSheetBehavior.BottomSheetCallback() {
            @Override
            public void onStateChanged(@NonNull View bottomSheet, int newState) {
                //拖动
            }

            @Override
            public void onSlide(@NonNull View bottomSheet, float slideOffset) {
                //状态变化
            }
        });
    }
}
```

* 在设备屏幕旋转时BottomSheetDialog会消失，通过在`AndroidManifest.xml`设置`configChanges`可以避免

```xml
        <activity
            android:name=".SecondActivity"
            android:configChanges="orientation" />
```

至此，简单的通过BottomSheetBehavior实现BottomSheetDialog就结束了，更复杂的效果是添加RecyclerView到BottomSheetDialog
中，同时增加点击事件监听等等，接下来介绍如何动态使用BottomSheetDialog。

### Modal BottomSheetDialog

如果你使用过AlertDialog那么就应该知道了，动态调用就是直接new一个出来，然后show一下就完事了，同理对BottomSheetDialog也成立，
因此不需要固定的BottomSheetBehavior，而直接new也分为两种方式，一个是`new BottomSheetDialog()`，另一个是`new BottomSheetDialog()`，
两者显示效果相同，但是后者通过fragment控制生命周期更合理，所以使用后者，简单使用的话只需要三步：

1. 继承自**BottomSheetDialogFragment**；
2. 重写**onCreateView**方法，加入你自定义的布局；
3. 调用**show**方法，这里需要**Activity.getSupportFragmentManager()**。

{% asset_img design1.png %}

我这里实现一个相对复杂的布局，如上图所示，具体包括两部分，一个是header，header可以是一个自定义view，也可以将header隐藏，header与下面的Menu之间是透明的，下面的Menu通过RecyclerView控制选项数量，点击单个选项有水波纹效果，代码如下：

* 首先是Dialog的布局文件`dialog_option.xml`，根据上面的描述就知道是一个RecyclerView

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/forget_psw_bottom_sheet_layout"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/menu_list"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

</LinearLayout>
```

* 然后是需要实现这个Dialog为透明背景，这是因为header也在RecyclerView中，那么只有透明背景才可以实现header悬浮的效果，Dialog透明背景需要styles文件

```xml
    <style name="SheetDialog" parent="Theme.Design.Light.BottomSheetDialog">
        <!-- 关键属性是colorBackground，transparent可以是背景透明，但是这会导致一个问题，此处伏笔 -->
        <item name="android:windowIsTranslucent">true</item>
        <item name="android:windowContentOverlay">@null</item>
        <item name="android:colorBackground">@android:color/transparent</item>
        <item name="android:backgroundDimEnabled">true</item>
        <item name="android:backgroundDimAmount">0.3</item>
        <item name="android:windowFrame">@null</item>
        <item name="android:windowIsFloating">true</item>
    </style>
```

* 以及header的布局文件`card_layout.xml`和Menu Item的布局文件`menu_item.xml`，header有圆角，可以用另一种Material组件实现CardView

```xml
<!-- card_layout.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:padding="8dp">

    <androidx.cardview.widget.CardView
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_margin="4dp"
        android:layout_weight="1"
        android:elevation="4dp"
        app:cardCornerRadius="10dp">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:background="@color/white"
            android:orientation="horizontal"
            android:padding="12dp">

            <TextView
                style="@style/Image"
                android:text="@string/glass" />

            <TextView
                style="@style/Image"
                android:text="@string/clap" />

            <TextView
                style="@style/Image"
                android:text="@string/cry" />

            <TextView
                style="@style/Image"
                android:text="@string/party" />

            <TextView
                style="@style/Image"
                android:text="@string/heart" />

            <TextView
                style="@style/Image"
                android:text="@string/thumb" />

            <ImageView
                style="@style/Image"
                android:src="@drawable/ic_keyboard_arrow_right_black_24dp" />
        </LinearLayout>

    </androidx.cardview.widget.CardView>

    <androidx.cardview.widget.CardView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_margin="4dp"
        android:elevation="4dp"
        app:cardCornerRadius="10dp">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:background="@color/white"
            android:orientation="horizontal"
            android:padding="12dp">

            <ImageView
                android:layout_width="20dp"
                android:layout_height="20dp"
                android:layout_gravity="center"
                android:src="@drawable/outline" />
        </LinearLayout>

    </androidx.cardview.widget.CardView>
</LinearLayout>
```

这里使用了strings的资源，通过Unicode表示表情符号

```xml
<resources>
    <string name="thumb">&#128532;</string>
    <string name="heart">❤️</string>
    <string name="party">&#128222;</string>
    <string name="cry">&#128722;</string>
    <string name="clap">&#128512;</string>
    <string name="glass">&#128522;</string>
</resources>
```

```xml
<!-- menu_item.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content">

    <!-- 注意这里伏笔就来了，设置为透明背景的Dialog中，子控件也会是透明的，而且若对子控件的background
    设置为某种颜色则无法产生水波纹效果，所以需要自定义@drawable/touch_bg -->
    <TextView
        android:id="@+id/menu_text"
        style="@style/BottomDialog"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:background="@drawable/touch_bg" />
</LinearLayout>
```

```xml
    <style name="BottomDialog">
        <item name="android:padding">16dp</item>
        <item name="android:textSize">16sp</item>
        <item name="android:textColor">@color/black</item>
        <item name="android:gravity">center</item>
        <item name="android:textStyle">normal</item>
    </style>
```

```xml
<!-- touch_bg.xml -->
<?xml version="1.0" encoding="utf-8"?>
<!--Use an almost transparent color for the ripple itself-->
<ripple xmlns:android="http://schemas.android.com/apk/res/android"
android:color="#22000000">

<!--Use this to define the shape of the ripple effect (rectangle, oval, ring or line). 
The color specified here isn't used anyway-->
<item android:id="@android:id/mask">
    <shape android:shape="rectangle">
        <solid android:color="#000000" />
    </shape>
</item>

<!--This is the background for your button-->
<item>
    <!--Use the shape you want here-->
    <shape android:shape="rectangle">
        <!--Use the solid tag to define the background color you want (here white)-->
        <solid android:color="@color/white"/>
        <!--Use the stroke tag for a border-->
        <stroke android:width="1dp" android:color="@color/white"/>
    </shape>
</item>
</ripple>
```

* 接下来就是主要java代码了，包括`MenuBottomSheetDialog.java`和`MenuListAdapter.java`，前者是我们最终调用的Dialog，后者是RecyclerView的Adapter，以及自定义一个Menu Item的实体类`OptionMenuItem.java`用于保存信息

```java
public class OptionMenuItem {
    // label表示选项的名称最终会显示在Dialog，action表示该选项的行为，这里可以自定义增加其他内容，
    // 比如增加一个state属性表示该选项是否可用等等，如不可用，则颜色为灰色且不可点击，不过我没加
    private String label;
    private int action;

    public OptionMenuItem(String label, int action) {
        this.label = label;
        this.action = action;
    }

    public String getLabel() {
        return label;
    }

    public void setLabel(String label) {
        this.label = label;
    }

    public int getAction() {
        return action;
    }

    public void setAction(int action) {
        this.action = action;
    }
}
```

```java
public class MenuBottomSheetDialog extends BottomSheetDialogFragment {

    private static final String TAG = MenuBottomSheetDialog.class.getSimpleName();

    private RecyclerView recyclerView;

    private MenuListAdapter adapter;
    // 这里还加了一个参数hasItemDecoration用于控制是否显示选项之间的分割线
    private Boolean hasItemDecoration = true;

    private Context context;

    private static MenuBottomSheetDialog newInstance(Builder builder) {
        MenuBottomSheetDialog fragment = new MenuBottomSheetDialog();
//        Bundle bundle = new Bundle();
//        fragment.setArguments(bundle);
        fragment.setHasItemDecoration(builder.hasItemDecoration);
        fragment.setAdapter(builder.adapter);
        fragment.setContext(builder.context);
        return fragment;
    }

    @NonNull
    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        // R.style.SheetDialog 透明背景需要在onCreateDialog方法引入
        return new BottomSheetDialog(context, R.style.SheetDialog);
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, 
                              @Nullable Bundle savedInstanceState) {
        // 在onCreateView引入定义的dialog布局
        return inflater.inflate(R.layout.dialog_option, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        // onViewCreated中进行初始化，这里就很简单的使用了RecyclerView
        recyclerView = view.findViewById(R.id.menu_list);
        recyclerView.setLayoutManager(new LinearLayoutManager(getContext()));
        recyclerView.setAdapter(adapter);
        if (hasItemDecoration) {
            // DividerItemDecoration可以方便的加入到RecyclerView，形成分割线，布局文件在下面
            DividerItemDecoration dec = new DividerItemDecoration(context, DividerItemDecoration.VERTICAL);
            dec.setDrawable(getResources().getDrawable(R.drawable.divider_line));
            recyclerView.addItemDecoration(dec);
        }
    }
    // 最终我们通过show方法调用
    public void show(FragmentManager fragmentManager) {
        FragmentTransaction transaction = fragmentManager.beginTransaction();
        Fragment prevFragment = fragmentManager.findFragmentByTag(TAG);
        if (prevFragment != null) {
            transaction.remove(prevFragment);
        }
        transaction.addToBackStack(null);
        show(transaction, TAG);
    }
    // 这里因为参数可能会有很多，所以采用建造者模式实现
    public static Builder builder(Context context) {
        return new Builder(context);
    }

    public static class Builder {
        // 建造者模式需要传入的参数有三个
        private MenuListAdapter adapter;
        private Boolean hasItemDecoration;
        private Context context;

        public Builder(Context context) {
            this.context = context;
        }

        // 以下都是建造者模式可调用的方法
        public Builder setAdapter(MenuListAdapter adapter) {
            this.adapter = adapter;
            return this;
        }

        public Builder setHasItemDecoration(Boolean hasItemDecoration) {
            this.hasItemDecoration = hasItemDecoration;
            return this;
        }

        public MenuBottomSheetDialog build() {
            return newInstance(this);
        }

        public MenuBottomSheetDialog show(FragmentManager fragmentManager) {
            MenuBottomSheetDialog dialog = build();
            dialog.show(fragmentManager);
            return dialog;
        }
    }

    private void setAdapter(MenuListAdapter adapter) {
        this.adapter = adapter;
    }

    private void setContext(Context context) {
        this.context = context;
    }

    private void setHasItemDecoration(Boolean hasItemDecoration) {
        this.hasItemDecoration = hasItemDecoration;
    }
}
```

```xml
<!-- divider_line.xml -->
<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <!--分割线左右边距-->
    <item>
        <shape>
            <solid android:color="@color/split_line_grey" />
            <size android:height="1dp" />
        </shape>
    </item>
</layer-list>

```

* 接下来是RecyclerView的Adapter文件`MenuListAdapter.java`

```java
public class MenuListAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    // 通过hasHeader控制是否显示header，这里是通过MenuListAdapter传入的参数，没有用上面建造者模式
    private Boolean hasHeader;
    // 监听选项点击，这里我仅仅对选项做监听没有对header进行任何控制，所以header只是个没有灵魂的花瓶
    private OnMenuItemClickListener onMenuClickListener;
    // 传入的选项list
    private List<OptionMenuItem> options;
    // onCreateViewHolder判断是否为header的参数
    public static final int VIEW_TYPE_HEADER = 0;

    public static final int VIEW_TYPE_ITEM = 1;

    public MenuListAdapter() {
        this.options = new ArrayList<>();
    }

    public MenuListAdapter(List<OptionMenuItem> options) {
        this.options = options;
    }

    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        RecyclerView.ViewHolder viewHolder = null;
        switch (viewType) {
            // 这里也比较好理解，如果为header传入header的布局，如果为Menu Item则传入Item的布局
            case VIEW_TYPE_HEADER:
                viewHolder = new HeaderViewHolder(LayoutInflater.from(parent.getContext()).inflate(R.layout.card_layout, parent, false));
                break;
            case VIEW_TYPE_ITEM:
                viewHolder = new MenuItemViewHolder(LayoutInflater.from(parent.getContext()).inflate(R.layout.menu_item, parent, false));
                break;
        }
        return viewHolder;
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        switch (holder.getItemViewType()) {
            case VIEW_TYPE_HEADER:
                // todo add header view listener
                break;
            case VIEW_TYPE_ITEM:
                // 注意这里positon与header存在与否的关系，然后通过接口把点击事件传出去
                OptionMenuItem menuItem = options.get(hasHeader ? position - 1 : position);
                ((MenuItemViewHolder) holder).bind(menuItem);
                holder.itemView.setOnClickListener(v -> {
                    Log.i("aaa", "click");
                    if (onMenuClickListener != null) {
                        onMenuClickListener.onMenuClick(holder.itemView, menuItem.getAction());
                    }
                });
                break;
        }
    }

    @Override
    public int getItemViewType(int position) {
        // 在getItemViewType定义type，从而在前面两个方法中获取
        if (hasHeader) {
            if (position == 0) {
                return VIEW_TYPE_HEADER;
            }
        }
        return VIEW_TYPE_ITEM;
    }

    @Override
    public int getItemCount() {
        // 同理options.size()与hasHeader的关系
        return hasHeader ?
                (options.size() + 1) : options.size();
    }

    class MenuItemViewHolder extends RecyclerView.ViewHolder {
        TextView text;
        // 正如我在Menu Item实体类中所设想的，我们可以在这里根据state进行额外的控制
        public MenuItemViewHolder(@NonNull View itemView) {
            super(itemView);
            text = itemView.findViewById(R.id.menu_text);
        }

        private void bind(OptionMenuItem optionMenuItem) {
            text.setText(optionMenuItem.getLabel());
        }
    }

    class HeaderViewHolder extends RecyclerView.ViewHolder {

        public HeaderViewHolder(@NonNull View itemView) {
            super(itemView);
        }
    }

    public void addAll(List<OptionMenuItem> options) {
        this.options.clear();
        this.options.addAll(options);
        notifyDataSetChanged();
    }

    public void add(OptionMenuItem option) {
        if (options != null) {
            this.options.add(option);
            notifyDataSetChanged();
        }
    }

    public void setHasHeader(Boolean hasHeader) {
        this.hasHeader = hasHeader;
    }
    
    // 对外暴露的接口以及设置监听的方法
    public interface OnMenuItemClickListener {
        void onMenuClick(View view, int action);
    }

    public void setOnMenuItemClickListener(OnMenuItemClickListener listener) {
        this.onMenuClickListener = listener;
    }
}

```

* 最后是直接使用的方式`ThirdActivity.java`

```java
public class ThirdActivity extends AppCompatActivity implements MenuListAdapter.OnMenuItemClickListener{

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_third);

        ArrayList<OptionMenuItem> list = new ArrayList<>();
        list.add(new OptionMenuItem("Forward", 98));
        list.add(new OptionMenuItem("Copy", 2121));
        list.add(new OptionMenuItem("Mark as unread", 111));
        list.add(new OptionMenuItem("Star message", 66));
        list.add(new OptionMenuItem("Cancel", 2));

        MenuListAdapter menuListAdapter = new MenuListAdapter();
        menuListAdapter.addAll(list);
        menuListAdapter.setHasHeader(true);
        menuListAdapter.setOnMenuItemClickListener(this);

        findViewById(R.id.button2).setOnClickListener(v -> {
            // 两种方式等效
            // MenuBottomSheetDialog.builder(ThirdActivity.this)
            //         .setAdapter(menuListAdapter)
            //         .setHasItemDecoration(true)
            //         .show(getSupportFragmentManager());

            MenuBottomSheetDialog dialog = MenuBottomSheetDialog.builder(ThirdActivity.this)
                    .setAdapter(menuListAdapter)
                    .setHasItemDecoration(true)
                    .build();
            dialog.show(getSupportFragmentManager());
        });

    }

    @Override
    public void onMenuClick(View view, int action) {
        // 点击事件的回调
        Toast.makeText(this, "action " + action, Toast.LENGTH_SHORT).show();
    }
}
```

## 3. BottomSheetDialog进阶与Bug

{% asset_img design2.gif %}

上图即BottomSheetDialog与ViewPager以及RecyclerView之间的Bug，简而言之就是ViewPager下除了第一个页面可以滑动之外，其他页面均不可滑动，具体的[Error link](https://stackoverflow.com/questions/39326321/scroll-not-working-for-multiple-recyclerview-in-bottomsheet?noredirect=1&lq=1)以及我在Github上提的[issue](https://github.com/material-components/material-components-android/issues/373)，这个问题已经有大神给出了解决方法，但是官方目前还是没有引入。

下面我们就来复现这种状况

