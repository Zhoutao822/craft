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

下面我们就来复现这种状况，不过我的设计效果与上图略有不同，增加了一些内容，首先是TabLayout的title，它是由两部分组成，前面是一个Unicode表情，后面是数字，数值表示在这个表情下的list的大小；TabLayout下面对应不同的Fragment，Fragment中显示当前的list，我这里生成的Item都是简单写一下，没有具体意义；整个设计思路是，自定义一个`ListBottomSheetDialog`，这个dialog由ViewPager + TabLayout + Fragment + RecyclerView组成，先从Fragment开始实现步骤

{% asset_img design3.png %}

* `ListObjectFragment`布局文件`fragment_list.xml`与Item布局文件`item_list.xml`

```xml
<!-- fragment_list.xml -->
<!-- 首先暂时使用CoordinatorLayout，可能后续会修改为NestedScrollView，此处伏笔 -->
<!-- 而且background="@color/white"是由于后面Dialog为透明背景，这里需要白色背景避免Fragment切换时背景突变透明 -->
<?xml version="1.0" encoding="utf-8"?>
<androidx.coordinatorlayout.widget.CoordinatorLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/white"
    android:orientation="vertical">

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/list_view"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:layout_behavior="com.google.android.material.bottomsheet.BottomSheetBehavior" />

</androidx.coordinatorlayout.widget.CoordinatorLayout>
```

```xml
<!-- item_list.xml -->
<!-- 注意这里也使用了上面文中出现的水波纹效果背景touch_bg，这是因为要实现圆角背景 -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:background="@drawable/touch_bg"
    android:orientation="horizontal"
    android:padding="10dp">

    <ImageView
        android:id="@+id/avatar"
        android:layout_width="40dp"
        android:layout_height="40dp"
        android:background="@color/holo_blue_light" />

    <TextView
        android:id="@+id/name"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:layout_marginStart="10dp"
        android:layout_weight="1"
        android:padding="5dp"
        android:text="name"
        android:textColor="@color/black"
        android:textSize="20sp" />

</LinearLayout>
```

* 然后是RecyclerView的Adapter `ListViewAdapter.java`

```java
public class ListViewAdapter extends RecyclerView.Adapter<ListViewAdapter.MyViewHolder>{
    // 这里加了点击事件的接口
    private ItemClickListener onItemClickListener;
    // 显示的Item就是一个一个的User信息，User信息也很简单，avatar和name，但是avatar没有赋值
    private List<User> data;

    public ListViewAdapter(List<User> data) {
        this.data = data;
    }

    @NonNull
    @Override
    public MyViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        // 常见方式
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_list, parent, false);
        MyViewHolder holder = new MyViewHolder(view);
        return holder;
    }

    @Override
    public void onBindViewHolder(@NonNull MyViewHolder holder, int position) {
        User user = data.get(position);
        // 这里avatar写死了，没有赋值，偷个懒
        holder.avatar.setImageResource(R.drawable.ic_launcher_foreground);
        holder.name.setText(user.getName());
        // 把点击事件传出去
        holder.itemView.setOnClickListener(v -> {
            if (onItemClickListener != null) {
                onItemClickListener.onItemClick(holder.itemView, position);
            }
        });
    }

    @Override
    public int getItemCount() {
        return data.size();
    }

    class MyViewHolder extends RecyclerView.ViewHolder {
        ImageView avatar;
        TextView name;

        public MyViewHolder(@NonNull View itemView) {
            super(itemView);
            avatar = itemView.findViewById(R.id.avatar);
            name = itemView.findViewById(R.id.name);
        }
    }

    public interface ItemClickListener {
        void onItemClick(View view, int position);
    }

    public void setItemClickListener(ItemClickListener clickListener) {
        onItemClickListener = clickListener;
    }
}
```

```java
public class User {
    private String avatar;
    private String name;

    public User(String avatar, String name) {
        this.avatar = avatar;
        this.name = name;
    }

    public String getAvatar() {
        return avatar;
    }

    public void setAvatar(String avatar) {
        this.avatar = avatar;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
```

* Fragment `ListObjectFragment.java`

```java
public class ListObjectFragment extends Fragment implements ListViewAdapter.ItemClickListener{
    // emoji表示Unicode表情，count表示list大小
    private int count;
    private String emoji;
    private List<User> list;
    private ListViewAdapter listViewAdapter;
    private RecyclerView recyclerView;

    // 加了几个参数用于仅在Fragment对用户可见时加载数据，针对ViewPager预加载
    private boolean isViewInitiated;
    private boolean isVisibleToUser;
    private boolean isDataInitiated;

    // 这里传入了list，但是在onResume时才是真实加载数据的时候
    public ListObjectFragment(String emoji, int count, List<User> list) {
        this.emoji = emoji;
        this.count = count;
        this.list = list;
    }

    @Override
    public View onCreateView(LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_list_test, container, false);
    }

    @Override
    public void onResume() {
        super.onResume();
        isVisibleToUser = true;
        prepareFetchData();
        listViewAdapter = new ListViewAdapter(list);
        listViewAdapter.setItemClickListener(this);
        recyclerView.setLayoutManager(new LinearLayoutManager(getContext()));
        recyclerView.setAdapter(listViewAdapter);
    }

    @Override
    public void onStop() {
        super.onStop();
        isVisibleToUser = false;
    }

    private void fetchData() {
        // 真实加载list的地方，这里仅模拟
        list = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            list.add(new User("", "name" + i));
        }
    }

    public boolean prepareFetchData() {
        return prepareFetchData(false);
    }

    public boolean prepareFetchData(boolean forceUpdate) {
        if (isVisibleToUser && isViewInitiated && (!isDataInitiated || forceUpdate)) {
            fetchData();
            isDataInitiated = true;
            return true;
        }
        return false;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        isViewInitiated = true;
        recyclerView = view.findViewById(R.id.list_view);
    }

    @Override
    public void onItemClick(View view, int position) {
        // 点击事件回调
        Toast.makeText(getContext(), "position" + position, Toast.LENGTH_SHORT).show();
    }
}
```

* 自定义BottomSheetDialog的布局文件`dialog_list.xml`，圆角背景`radius_background.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <com.google.android.material.tabs.TabLayout
        android:id="@+id/tablayout"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:background="@drawable/radius_background"
        app:tabIndicatorColor="@color/colorPrimaryDark"
        app:tabMode="scrollable"
        app:tabTextColor="@color/black" />

    <View
        android:layout_width="match_parent"
        android:layout_height="1dp"
        android:background="@color/split_line_grey" />

    <com.tao.bottomsheetdemo.custom.CustomViewPager
        android:id="@+id/viewpager"
        android:layout_width="match_parent"
        android:layout_height="match_parent"/>

</LinearLayout>
```

```xml
<!-- radius_background.xml -->
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="@color/white" />
    <corners
        android:topLeftRadius="10dp"
        android:topRightRadius="10dp" />
</shape>
```

* 自定义ViewPager `CustomViewPager.java`

```java
public class CustomViewPager extends ViewPager {
    // CustomViewPager control scroll enable
    private boolean enabled;

    public CustomViewPager(@NonNull Context context) {
        super(context);
        this.enabled = true;
    }

    public CustomViewPager(Context context, AttributeSet attrs) {
        super(context, attrs);
        this.enabled = true;
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        if (this.enabled) {
            return super.onTouchEvent(event);
        }
        return false;
    }

    @Override
    public boolean onInterceptTouchEvent(MotionEvent event) {
        // 事件传递控制是否支持左右滑动
        if (this.enabled) {
            return super.onInterceptTouchEvent(event);
        }
        return false;
    }

    public void setPagingEnabled(boolean enabled) {
        this.enabled = enabled;
    }
}

```

* 自定义BottomSheetDialog `ListBottomSheetDialog.java`与ViewPager的Adapter `ListPagerAdapter.java`

```java
public class ListBottomSheetDialog extends BottomSheetDialogFragment {

    private static final String TAG = ListBottomSheetDialog.class.getSimpleName();

    // 这里的ViewPager为自定义的CustomViewPager，多了额外的功能：可以控制是否支持左右滑动切换Fragment
    private TabLayout tabLayout;
    private CustomViewPager viewPager;
    // offscreenPageLimit设置可以使ViewPager下的Fragment缓存数据，数值表示缓存数据的Fragment数量
    private int offscreenPageLimit = 10;
    // 通过参数控制是否支持左右滑动
    private Boolean enableScroll;
    // EmojiItem是包含emoji/count/list的实体类，所以可知传入Dialog的数据是一种嵌套list形式
    private List<EmojiItem> emojiItemList;

    private Context context;
    // ViewPager的Adapter
    private ListPagerAdapter adapter;

    private static ListBottomSheetDialog newInstance(ListBottomSheetDialog.Builder builder) {
        ListBottomSheetDialog fragment = new ListBottomSheetDialog();
//        Bundle bundle = new Bundle();
//        fragment.setArguments(bundle);
//        fragment.setHeight(builder.peekHeight, builder.maxHeight);
        fragment.setEmojiItemList(builder.emojiItemList);
        fragment.setContext(builder.context);
        fragment.setOffscreenPageLimit(builder.offscreenPageLimit);
        fragment.setEnableScroll(builder.enableScroll);
        return fragment;
    }

    @NonNull
    @Override
    public Dialog onCreateDialog(@Nullable Bundle savedInstanceState) {
//      由于需要首先圆角背景，所以这里也使用了透明背景  
        BottomSheetDialog dialog = new BottomSheetDialog(context, R.style.SheetDialog);
//        set dialog peek height and max height
//        dialog.setPeekHeight(peekHeight);
//        dialog.setMaxHeight(maxHeight);
        return dialog;
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.dialog_list, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        viewPager = view.findViewById(R.id.viewpager);
        tabLayout = view.findViewById(R.id.tablayout);
        if (viewPager != null && tabLayout != null) {
            initViewPager();
        }
    }

    private void initViewPager() {
        // ListPagerAdapter.BEHAVIOR_RESUME_ONLY_CURRENT_FRAGMENT参数控制仅在Fragment对用户可见时调用onResume，这也是对应了上面在
        // Fragment中数据加载
        adapter = new ListPagerAdapter(getChildFragmentManager(), ListPagerAdapter.BEHAVIOR_RESUME_ONLY_CURRENT_FRAGMENT, context);
        // 这里的emojiItemList比较简单，没有其他参数，理论上需要根据定义的其他参数传入到Fragment中再进行进一步请求数据
        adapter.setEmojiItemList(emojiItemList);
        viewPager.setAdapter(adapter);
        viewPager.setOffscreenPageLimit(offscreenPageLimit);
        // 这里可以控制是否左右滑动
        viewPager.setPagingEnabled(enableScroll);
        // TabLayout与ViewPager关联，自动实现滑动切换或者点击切换的效果
        tabLayout.setupWithViewPager(viewPager);
    }

    public void show(FragmentManager fragmentManager) {
        FragmentTransaction transaction = fragmentManager.beginTransaction();
        Fragment prevFragment = fragmentManager.findFragmentByTag(TAG);
        if (prevFragment != null) {
            transaction.remove(prevFragment);
        }
        transaction.addToBackStack(null);
        show(transaction, TAG);
    }

    // 建造者模式，同上
    public static Builder builder(Context context) {
        return new Builder(context);
    }

    public static class Builder {

        // private int peekHeight;
        // private int maxHeight;
        private int offscreenPageLimit;
        private Boolean enableScroll;
        private List<EmojiItem> emojiItemList;
        private Context context;

        public Builder(Context context) {
            this.context = context;
        }
        // 这里注释掉的方法可以控制Dialog Expand状态下的高度以及Collapse状态的高度，但是需要自定义BottomSheetDialog
        // 暂时不写
        // public Builder setPeekHeight(int peekHeight) {
        //     this.peekHeight = peekHeight;
        //     return this;
        // }

        // public Builder setMaxHeight(int maxHeight) {
        //     this.maxHeight = maxHeight;
        //     return this;
        // }

        public Builder setOffscreenPageLimit(int offscreenPageLimit) {
            this.offscreenPageLimit = offscreenPageLimit;
            return this;
        }

        public Builder setEnableScroll(Boolean enableScroll) {
            this.enableScroll = enableScroll;
            return this;
        }

        public Builder setEmojiItemList(List<EmojiItem> emojiItemList) {
            this.emojiItemList = emojiItemList;
            return this;
        }

        public ListBottomSheetDialog build() {
            return newInstance(this);
        }

        public ListBottomSheetDialog show(FragmentManager fragmentManager) {
            ListBottomSheetDialog dialog = build();
            dialog.show(fragmentManager);
            return dialog;
        }
    }

    private void setContext(Context context) {
        this.context = context;
    }

    // private void setHeight(int peekHeight, int maxHeight) {
    //     this.peekHeight = peekHeight;
    //     this.maxHeight = maxHeight;
    // }

    private void setOffscreenPageLimit(int offscreenPageLimit) {
        this.offscreenPageLimit = offscreenPageLimit;
    }

    private void setEnableScroll(Boolean enableScroll) {
        this.enableScroll = enableScroll;
    }

    private void setEmojiItemList(List<EmojiItem> emojiItemList) {
        this.emojiItemList = emojiItemList;
    }

}
```

```java
public class ListPagerAdapter extends FragmentStatePagerAdapter {

    private List<EmojiItem> emojiItemList;

    private List<EmojiItem> sortedList;

    private Context context;

    public ListPagerAdapter(@NonNull FragmentManager fm, int behavior, Context context) {
        super(fm, behavior);
        this.context = context;
    }

    public ListPagerAdapter(@NonNull FragmentManager fm, int behavior, List<EmojiItem> emojiItemList, Context context) {
        super(fm, behavior);
        this.emojiItemList = emojiItemList;
        this.context = context;
        // 这里还需要将传入的emojiItemList按照count进行降序排列
        this.sortedList = sortList(emojiItemList);
    }

    @Override
    public Fragment getItem(int position) {
        String label = sortedList.get(position).getEmoji();
        int count = sortedList.get(position).getCount();
        List<User> list = sortedList.get(position).getUserList();
        Fragment fragment = new ListObjectFragment(label, count, list);
        Bundle args = new Bundle();
        return fragment;
    }

    @Override
    public int getCount() {
        return emojiItemList.size();
    }

    @Override
    public CharSequence getPageTitle(int position) {
        // 这里设置TabLayout的title，emoji+count
        CharSequence emoji = sortedList.get(position).getEmoji();
        CharSequence title = emoji + " " + sortedList.get(position).getCount();
        SpannableStringBuilder spBuilder = new SpannableStringBuilder(title);
        Pattern pattern = Pattern.compile(emoji.toString());
        Matcher matcher = pattern.matcher(title);
        while (matcher.find()) {
            TextAppearanceSpan span = new TextAppearanceSpan(context, R.style.UIKitTextView_ReactionLabel);
            spBuilder.setSpan(span, matcher.start(), matcher.end(), Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
        }
        return spBuilder;
    }

    private List<EmojiItem> sortList(List<EmojiItem> list) {
        List<EmojiItem> tmp = new ArrayList<>(list);
        Collections.sort(tmp, new Comparator<EmojiItem>() {
            @Override
            public int compare(EmojiItem o1, EmojiItem o2) {
                return o2.getCount() - o1.getCount();
            }
        });
        return tmp;
    }

    public void setEmojiItemList(List<EmojiItem> emojiItemList) {
        this.emojiItemList = emojiItemList;
        this.sortedList = sortList(emojiItemList);
    }
}
```

* EmojiItem实体类

```java
public class EmojiItem {

    private String emoji;
    private int count;
    private List<User> userList;

    public EmojiItem(String emoji, int count, List<User> userList) {
        this.emoji = emoji;
        this.count = count;
        this.userList = userList;
    }

    public String getEmoji() {
        return emoji;
    }

    public void setEmoji(String emoji) {
        this.emoji = emoji;
    }

    public int getCount() {
        return count;
    }

    public void setCount(int count) {
        this.count = count;
    }

    public List<User> getUserList() {
        return userList;
    }

    public void setUserList(List<User> userList) {
        this.userList = userList;
    }
}
```

* 调用 `FourthActivity.java`

```java
public class FourthActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_fourth);
        List<EmojiItem> data = new ArrayList<>();
        String[] arr = new String[]{
                "\uD83D\uDC4D", "❤️", "\uD83C\uDF89", "\uD83D\uDE02", "\uD83D\uDC4F", "\uD83D\uDE0E"
        };
        for (int i = 0; i < arr.length; i++) {
            data.add(new EmojiItem(arr[i], i + 10, null));
        }

        findViewById(R.id.button4).setOnClickListener(v ->
                ListBottomSheetDialog.builder(FourthActivity.this)
                .setEmojiItemList(data)
                .setOffscreenPageLimit(5)
                .setEnableScroll(true)
                .show(getSupportFragmentManager()));
    }
}
```

**运行结果**

{% asset_img design4.gif %}

很明显有几个问题：

1. list上面有一段空白
2. 除了第一个Fragment中的list可以上下滑动以外，其他Fragment中的list不可滑动，这也就是BottomSheetDialog的bug

## 4. 解决方法

* 针对第一个Bug，这是由于Fragment的布局文件中采用了CoordinatorLayout，我们替换为NestedScrollView，对应伏笔。

* 第二个bug就比较复杂，根据找到的资料显示大致有两种解决方法（并不一定能成功）

### 4.1 重写ViewPager的Adapter的setPrimaryItem方法

也就是在`ListPagerAdapter.java`中加入

```java
    @Override
    public void setPrimaryItem(@NonNull ViewGroup container, int position, @NonNull Object object) {
        super.setPrimaryItem(container, position, object);
        Fragment currentFragment = (Fragment) object;
        if (currentFragment.getView() != null) {
            for (int i = 0; i < container.getChildCount(); i++) {
                if (i != position) {
                    // 注意这里用NestedScrollView是因为已经默认上面第一个bug被纠正
                    NestedScrollView otherScrollView = (NestedScrollView) container.getChildAt(i);
                    otherScrollView.setNestedScrollingEnabled(false);
                }
            }
            NestedScrollView currentNestedScrollView = (NestedScrollView) currentFragment.getView();
            currentNestedScrollView.setNestedScrollingEnabled(true);
            container.requestLayout();
        }
    }
```

这段代码的作用是让对用户可见的Fragment中的NestedScrollView设置为可以滑动，其他不可见为禁止滑动，但是很遗憾，并没有解决问题，不可滑动问题依然存在。

### 4.2 重写BottomSheetBehavior的findScrollingChild方法

我们可以对比以下原始的findScrollingChild方法

```java
  View findScrollingChild(View view) {
    if (ViewCompat.isNestedScrollingEnabled(view)) {
      return view;
    }
    if (view instanceof ViewGroup) {
      ViewGroup group = (ViewGroup) view;
      for (int i = 0, count = group.getChildCount(); i < count; i++) {
        View scrollingChild = findScrollingChild(group.getChildAt(i));
        if (scrollingChild != null) {
          return scrollingChild;
        }
      }
    }
    return null;
  }
```

以及修改后的findScrollingChild方法

```java
    private View findScrollingChild(View view) {
        if (ViewCompat.isNestedScrollingEnabled(view)) {
            return view;
        }
        // 修改后的代码增加了判断的选项，根据debug的结果我们知道如果最终返回的scrollingChild是可见状态的Fragment中的NestedScrollView，
        // 那么则可以正常滑动，否则不可滑动
        if (view instanceof ViewPager) {
            ViewPager viewPager = (ViewPager) view;
            // ViewPagerUtils通过反射获取position得到当前的Fragment中的NestedScrollView
            View currentViewPagerChild = ViewPagerUtils.getCurrentView(viewPager);
            if (currentViewPagerChild == null) {
                return null;
            }

            View scrollingChild = findScrollingChild(currentViewPagerChild);
            if (scrollingChild != null) {
                return scrollingChild;
            }
        } else if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0, count = group.getChildCount(); i < count; i++) {
                View scrollingChild = findScrollingChild(group.getChildAt(i));
                if (scrollingChild != null) {
                    return scrollingChild;
                }
            }
        }
        return null;
    }
```

为了重写findScrollingChild方法，有两种方式，一是在com.google.android.material.bottomsheet包下继承BottomSheetBehavior并重写findScrollingChild方法，一是创建新的BottomSheetBehavior类，复制其中的大部分代码以及相关文件。

1. 创建当前项目下的另一个包com.google.android.material.bottomsheet不是一个很好的选择，所以不采用；
2. 新建ViewPagerBottomSheetBehavior类，复制代码，并修改findScrollingChild方法，这样会创建很多额外的文件。

采用方法二，我们需要加入以下几个文件`ViewPagerBottomSheetBehavior.java`、`ViewPagerUtils.java`、`BottomSheetUtils.java`、`design_view_pager_bottom_sheet_dialog.xml`

```java
/**
 * An interaction behavior plugin for a child view of {@link CoordinatorLayout} to make it work as
 * a bottom sheet.
 */
public class ViewPagerBottomSheetBehavior<V extends View> extends CoordinatorLayout.Behavior<V> {

    /**
     * Callback for monitoring events about bottom sheets.
     */
    public abstract static class BottomSheetCallback {

        /**
         * Called when the bottom sheet changes its state.
         *
         * @param bottomSheet The bottom sheet view.
         * @param newState    The new state. This will be one of {@link #STATE_DRAGGING},
         *                    {@link #STATE_SETTLING}, {@link #STATE_EXPANDED},
         *                    {@link #STATE_COLLAPSED}, or {@link #STATE_HIDDEN}.
         */
        public abstract void onStateChanged(@NonNull View bottomSheet, @State int newState);

        /**
         * Called when the bottom sheet is being dragged.
         *
         * @param bottomSheet The bottom sheet view.
         * @param slideOffset The new offset of this bottom sheet within [-1,1] range. Offset
         *                    increases as this bottom sheet is moving upward. From 0 to 1 the sheet
         *                    is between collapsed and expanded states and from -1 to 0 it is
         *                    between hidden and collapsed states.
         */
        public abstract void onSlide(@NonNull View bottomSheet, float slideOffset);
    }

    /**
     * The bottom sheet is dragging.
     */
    public static final int STATE_DRAGGING = 1;

    /**
     * The bottom sheet is settling.
     */
    public static final int STATE_SETTLING = 2;

    /**
     * The bottom sheet is expanded.
     */
    public static final int STATE_EXPANDED = 3;

    /**
     * The bottom sheet is collapsed.
     */
    public static final int STATE_COLLAPSED = 4;

    /**
     * The bottom sheet is hidden.
     */
    public static final int STATE_HIDDEN = 5;

    /**
     * @hide
     */
    @RestrictTo(LIBRARY_GROUP)
    @IntDef({STATE_EXPANDED, STATE_COLLAPSED, STATE_DRAGGING, STATE_SETTLING, STATE_HIDDEN})
    @Retention(RetentionPolicy.SOURCE)
    public @interface State {
    }

    /**
     * Peek at the 16:9 ratio keyline of its parent.
     *
     * <p>This can be used as a parameter for {@link #setPeekHeight(int)}.
     * {@link #getPeekHeight()} will return this when the value is set.</p>
     */
    public static final int PEEK_HEIGHT_AUTO = -1;

    private static final float HIDE_THRESHOLD = 0.5f;

    private static final float HIDE_FRICTION = 0.1f;

    private float mMaximumVelocity;

    private int mPeekHeight;

    private boolean mPeekHeightAuto;

    private int mPeekHeightMin;

    int mMinOffset;

    int mMaxOffset;

    boolean mHideable;

    private boolean mSkipCollapsed;

    @State
    int mState = STATE_COLLAPSED;

    ViewDragHelper mViewDragHelper;

    private boolean mIgnoreEvents;

    private int mLastNestedScrollDy;

    private boolean mNestedScrolled;

    int mParentHeight;

    WeakReference<V> mViewRef;

    WeakReference<View> mNestedScrollingChildRef;

    private BottomSheetCallback mCallback;

    private VelocityTracker mVelocityTracker;

    int mActivePointerId;

    private int mInitialY;

    boolean mTouchingScrollingChild;

    /**
     * Default constructor for instantiating ViewPagerBottomSheetBehaviors.
     */
    public ViewPagerBottomSheetBehavior() {
    }

    /**
     * Default constructor for inflating ViewPagerBottomSheetBehaviors from layout.
     *
     * @param context The {@link Context}.
     * @param attrs   The {@link AttributeSet}.
     */
    public ViewPagerBottomSheetBehavior(Context context, AttributeSet attrs) {
        super(context, attrs);
        TypedArray a = context.obtainStyledAttributes(attrs,
                R.styleable.BottomSheetBehavior_Layout);
        TypedValue value = a.peekValue(R.styleable.BottomSheetBehavior_Layout_behavior_peekHeight);
        if (value != null && value.data == PEEK_HEIGHT_AUTO) {
            setPeekHeight(value.data);
        } else {
            setPeekHeight(a.getDimensionPixelSize(
                    R.styleable.BottomSheetBehavior_Layout_behavior_peekHeight, PEEK_HEIGHT_AUTO));
        }
        setHideable(a.getBoolean(R.styleable.BottomSheetBehavior_Layout_behavior_hideable, false));
        setSkipCollapsed(a.getBoolean(R.styleable.BottomSheetBehavior_Layout_behavior_skipCollapsed,
                false));
        a.recycle();
        ViewConfiguration configuration = ViewConfiguration.get(context);
        mMaximumVelocity = configuration.getScaledMaximumFlingVelocity();
    }

    @Override
    public Parcelable onSaveInstanceState(CoordinatorLayout parent, V child) {
        return new SavedState(super.onSaveInstanceState(parent, child), mState);
    }

    @Override
    public void onRestoreInstanceState(CoordinatorLayout parent, V child, Parcelable state) {
        SavedState ss = (SavedState) state;
        super.onRestoreInstanceState(parent, child, ss.getSuperState());
        // Intermediate states are restored as collapsed state
        if (ss.state == STATE_DRAGGING || ss.state == STATE_SETTLING) {
            mState = STATE_COLLAPSED;
        } else {
            mState = ss.state;
        }
    }

    @Override
    public boolean onLayoutChild(CoordinatorLayout parent, V child, int layoutDirection) {
        if (ViewCompat.getFitsSystemWindows(parent) && !ViewCompat.getFitsSystemWindows(child)) {
            ViewCompat.setFitsSystemWindows(child, true);
        }
        int savedTop = child.getTop();
        // First let the parent lay it out
        parent.onLayoutChild(child, layoutDirection);
        // Offset the bottom sheet
        mParentHeight = parent.getHeight();
        int peekHeight;
        if (mPeekHeightAuto) {
            if (mPeekHeightMin == 0) {
                mPeekHeightMin = parent.getResources().getDimensionPixelSize(
                        R.dimen.design_bottom_sheet_peek_height_min);
            }
            peekHeight = Math.max(mPeekHeightMin, mParentHeight - parent.getWidth() * 9 / 16);
        } else {
            peekHeight = mPeekHeight;
        }
        mMinOffset = Math.max(0, mParentHeight - child.getHeight());
        mMaxOffset = Math.max(mParentHeight - peekHeight, mMinOffset);
        if (mState == STATE_EXPANDED) {
            ViewCompat.offsetTopAndBottom(child, mMinOffset);
        } else if (mHideable && mState == STATE_HIDDEN) {
            ViewCompat.offsetTopAndBottom(child, mParentHeight);
        } else if (mState == STATE_COLLAPSED) {
            ViewCompat.offsetTopAndBottom(child, mMaxOffset);
        } else if (mState == STATE_DRAGGING || mState == STATE_SETTLING) {
            ViewCompat.offsetTopAndBottom(child, savedTop - child.getTop());
        }
        if (mViewDragHelper == null) {
            mViewDragHelper = ViewDragHelper.create(parent, mDragCallback);
        }
        mViewRef = new WeakReference<>(child);
        mNestedScrollingChildRef = new WeakReference<>(findScrollingChild(child));
        return true;
    }

    @Override
    public boolean onInterceptTouchEvent(CoordinatorLayout parent, V child, MotionEvent event) {
        if (!child.isShown()) {
            mIgnoreEvents = true;
            return false;
        }
        int action = event.getActionMasked();
        // Record the velocity
        if (action == MotionEvent.ACTION_DOWN) {
            reset();
        }
        if (mVelocityTracker == null) {
            mVelocityTracker = VelocityTracker.obtain();
        }
        mVelocityTracker.addMovement(event);
        switch (action) {
            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_CANCEL:
                mTouchingScrollingChild = false;
                mActivePointerId = MotionEvent.INVALID_POINTER_ID;
                // Reset the ignore flag
                if (mIgnoreEvents) {
                    mIgnoreEvents = false;
                    return false;
                }
                break;
            case MotionEvent.ACTION_DOWN:
                int initialX = (int) event.getX();
                mInitialY = (int) event.getY();
                View scroll = mNestedScrollingChildRef != null
                        ? mNestedScrollingChildRef.get() : null;
                if (scroll != null && parent.isPointInChildBounds(scroll, initialX, mInitialY)) {
                    mActivePointerId = event.getPointerId(event.getActionIndex());
                    mTouchingScrollingChild = true;
                }
                mIgnoreEvents = mActivePointerId == MotionEvent.INVALID_POINTER_ID &&
                        !parent.isPointInChildBounds(child, initialX, mInitialY);
                break;
        }
        if (!mIgnoreEvents && mViewDragHelper.shouldInterceptTouchEvent(event)) {
            return true;
        }
        // We have to handle cases that the ViewDragHelper does not capture the bottom sheet because
        // it is not the top most view of its parent. This is not necessary when the touch event is
        // happening over the scrolling content as nested scrolling logic handles that case.
        View scroll = mNestedScrollingChildRef.get();
        return action == MotionEvent.ACTION_MOVE && scroll != null &&
                !mIgnoreEvents && mState != STATE_DRAGGING &&
                !parent.isPointInChildBounds(scroll, (int) event.getX(), (int) event.getY()) &&
                Math.abs(mInitialY - event.getY()) > mViewDragHelper.getTouchSlop();
    }

    @Override
    public boolean onTouchEvent(CoordinatorLayout parent, V child, MotionEvent event) {
        if (!child.isShown()) {
            return false;
        }
        int action = event.getActionMasked();
        if (mState == STATE_DRAGGING && action == MotionEvent.ACTION_DOWN) {
            return true;
        }
        if (mViewDragHelper != null) {
            mViewDragHelper.processTouchEvent(event);
        }
        // Record the velocity
        if (action == MotionEvent.ACTION_DOWN) {
            reset();
        }
        if (mVelocityTracker == null) {
            mVelocityTracker = VelocityTracker.obtain();
        }
        mVelocityTracker.addMovement(event);
        // The ViewDragHelper tries to capture only the top-most View. We have to explicitly tell it
        // to capture the bottom sheet in case it is not captured and the touch slop is passed.
        if (action == MotionEvent.ACTION_MOVE && !mIgnoreEvents) {
            if (Math.abs(mInitialY - event.getY()) > mViewDragHelper.getTouchSlop()) {
                mViewDragHelper.captureChildView(child, event.getPointerId(event.getActionIndex()));
            }
        }
        return !mIgnoreEvents;
    }

    @Override
    public boolean onStartNestedScroll(CoordinatorLayout coordinatorLayout, V child,
                                       View directTargetChild, View target, int nestedScrollAxes) {
        mLastNestedScrollDy = 0;
        mNestedScrolled = false;
        return (nestedScrollAxes & ViewCompat.SCROLL_AXIS_VERTICAL) != 0;
    }

    @Override
    public void onNestedPreScroll(CoordinatorLayout coordinatorLayout, V child, View target, int dx,
                                  int dy, int[] consumed) {
        View scrollingChild = mNestedScrollingChildRef.get();
        if (target != scrollingChild) {
            return;
        }
        int currentTop = child.getTop();
        int newTop = currentTop - dy;
        if (dy > 0) { // Upward
            if (newTop < mMinOffset) {
                consumed[1] = currentTop - mMinOffset;
                ViewCompat.offsetTopAndBottom(child, -consumed[1]);
                setStateInternal(STATE_EXPANDED);
            } else {
                consumed[1] = dy;
                ViewCompat.offsetTopAndBottom(child, -dy);
                setStateInternal(STATE_DRAGGING);
            }
        } else if (dy < 0) { // Downward
            if (!target.canScrollVertically(-1)) {
                if (newTop <= mMaxOffset || mHideable) {
                    consumed[1] = dy;
                    ViewCompat.offsetTopAndBottom(child, -dy);
                    setStateInternal(STATE_DRAGGING);
                } else {
                    consumed[1] = currentTop - mMaxOffset;
                    ViewCompat.offsetTopAndBottom(child, -consumed[1]);
                    setStateInternal(STATE_COLLAPSED);
                }
            }
        }
        dispatchOnSlide(child.getTop());
        mLastNestedScrollDy = dy;
        mNestedScrolled = true;
    }

    @Override
    public void onStopNestedScroll(CoordinatorLayout coordinatorLayout, V child, View target) {
        if (child.getTop() == mMinOffset) {
            setStateInternal(STATE_EXPANDED);
            return;
        }
        if (mNestedScrollingChildRef == null || target != mNestedScrollingChildRef.get()
                || !mNestedScrolled) {
            return;
        }
        int top;
        int targetState;
        if (mLastNestedScrollDy > 0) {
            top = mMinOffset;
            targetState = STATE_EXPANDED;
        } else if (mHideable && shouldHide(child, getYVelocity())) {
            top = mParentHeight;
            targetState = STATE_HIDDEN;
        } else if (mLastNestedScrollDy == 0) {
            int currentTop = child.getTop();
            if (Math.abs(currentTop - mMinOffset) < Math.abs(currentTop - mMaxOffset)) {
                top = mMinOffset;
                targetState = STATE_EXPANDED;
            } else {
                top = mMaxOffset;
                targetState = STATE_COLLAPSED;
            }
        } else {
            top = mMaxOffset;
            targetState = STATE_COLLAPSED;
        }
        if (mViewDragHelper.smoothSlideViewTo(child, child.getLeft(), top)) {
            setStateInternal(STATE_SETTLING);
            ViewCompat.postOnAnimation(child, new SettleRunnable(child, targetState));
        } else {
            setStateInternal(targetState);
        }
        mNestedScrolled = false;
    }

    @Override
    public boolean onNestedPreFling(CoordinatorLayout coordinatorLayout, V child, View target,
                                    float velocityX, float velocityY) {
        return target == mNestedScrollingChildRef.get() &&
                (mState != STATE_EXPANDED ||
                        super.onNestedPreFling(coordinatorLayout, child, target,
                                velocityX, velocityY));
    }

    void invalidateScrollingChild() {
        final View scrollingChild = findScrollingChild(mViewRef.get());
        mNestedScrollingChildRef = new WeakReference<>(scrollingChild);
    }

    /**
     * Sets the height of the bottom sheet when it is collapsed.
     *
     * @param peekHeight The height of the collapsed bottom sheet in pixels, or
     *                   {@link #PEEK_HEIGHT_AUTO} to configure the sheet to peek automatically
     *                   at 16:9 ratio keyline.
     * @attr ref android.support.design.R.styleable#BottomSheetBehavior_Layout_behavior_peekHeight
     */
    public final void setPeekHeight(int peekHeight) {
        boolean layout = false;
        if (peekHeight == PEEK_HEIGHT_AUTO) {
            if (!mPeekHeightAuto) {
                mPeekHeightAuto = true;
                layout = true;
            }
        } else if (mPeekHeightAuto || mPeekHeight != peekHeight) {
            mPeekHeightAuto = false;
            mPeekHeight = Math.max(0, peekHeight);
            mMaxOffset = mParentHeight - peekHeight;
            layout = true;
        }
        if (layout && mState == STATE_COLLAPSED && mViewRef != null) {
            V view = mViewRef.get();
            if (view != null) {
                view.requestLayout();
            }
        }
    }

    /**
     * Gets the height of the bottom sheet when it is collapsed.
     *
     * @return The height of the collapsed bottom sheet in pixels, or {@link #PEEK_HEIGHT_AUTO}
     * if the sheet is configured to peek automatically at 16:9 ratio keyline
     * @attr ref android.support.design.R.styleable#BottomSheetBehavior_Layout_behavior_peekHeight
     */
    public final int getPeekHeight() {
        return mPeekHeightAuto ? PEEK_HEIGHT_AUTO : mPeekHeight;
    }

    /**
     * Sets whether this bottom sheet can hide when it is swiped down.
     *
     * @param hideable {@code true} to make this bottom sheet hideable.
     * @attr ref android.support.design.R.styleable#BottomSheetBehavior_Layout_behavior_hideable
     */
    public void setHideable(boolean hideable) {
        mHideable = hideable;
    }

    /**
     * Gets whether this bottom sheet can hide when it is swiped down.
     *
     * @return {@code true} if this bottom sheet can hide.
     * @attr ref android.support.design.R.styleable#BottomSheetBehavior_Layout_behavior_hideable
     */
    public boolean isHideable() {
        return mHideable;
    }

    /**
     * Sets whether this bottom sheet should skip the collapsed state when it is being hidden
     * after it is expanded once. Setting this to true has no effect unless the sheet is hideable.
     *
     * @param skipCollapsed True if the bottom sheet should skip the collapsed state.
     * @attr ref android.support.design.R.styleable#BottomSheetBehavior_Layout_behavior_skipCollapsed
     */
    public void setSkipCollapsed(boolean skipCollapsed) {
        mSkipCollapsed = skipCollapsed;
    }

    /**
     * Sets whether this bottom sheet should skip the collapsed state when it is being hidden
     * after it is expanded once.
     *
     * @return Whether the bottom sheet should skip the collapsed state.
     * @attr ref android.support.design.R.styleable#BottomSheetBehavior_Layout_behavior_skipCollapsed
     */
    public boolean getSkipCollapsed() {
        return mSkipCollapsed;
    }

    /**
     * Sets a callback to be notified of bottom sheet events.
     *
     * @param callback The callback to notify when bottom sheet events occur.
     */
    public void setBottomSheetCallback(BottomSheetCallback callback) {
        mCallback = callback;
    }

    /**
     * Sets the state of the bottom sheet. The bottom sheet will transition to that state with
     * animation.
     *
     * @param state One of {@link #STATE_COLLAPSED}, {@link #STATE_EXPANDED}, or
     *              {@link #STATE_HIDDEN}.
     */
    public final void setState(final @State int state) {
        if (state == mState) {
            return;
        }
        if (mViewRef == null) {
            // The view is not laid out yet; modify mState and let onLayoutChild handle it later
            if (state == STATE_COLLAPSED || state == STATE_EXPANDED ||
                    (mHideable && state == STATE_HIDDEN)) {
                mState = state;
            }
            return;
        }
        final V child = mViewRef.get();
        if (child == null) {
            return;
        }
        // Start the animation; wait until a pending layout if there is one.
        ViewParent parent = child.getParent();
        if (parent != null && parent.isLayoutRequested() && ViewCompat.isAttachedToWindow(child)) {
            child.post(new Runnable() {
                @Override
                public void run() {
                    startSettlingAnimation(child, state);
                }
            });
        } else {
            startSettlingAnimation(child, state);
        }
    }

    /**
     * Gets the current state of the bottom sheet.
     *
     * @return One of {@link #STATE_EXPANDED}, {@link #STATE_COLLAPSED}, {@link #STATE_DRAGGING},
     * {@link #STATE_SETTLING}, and {@link #STATE_HIDDEN}.
     */
    @State
    public final int getState() {
        return mState;
    }

    void setStateInternal(@State int state) {
        if (mState == state) {
            return;
        }
        mState = state;
        View bottomSheet = mViewRef.get();
        if (bottomSheet != null && mCallback != null) {
            mCallback.onStateChanged(bottomSheet, state);
        }
    }

    private void reset() {
        mActivePointerId = ViewDragHelper.INVALID_POINTER;
        if (mVelocityTracker != null) {
            mVelocityTracker.recycle();
            mVelocityTracker = null;
        }
    }

    boolean shouldHide(View child, float yvel) {
        if (mSkipCollapsed) {
            return true;
        }
        if (child.getTop() < mMaxOffset) {
            // It should not hide, but collapse.
            return false;
        }
        final float newTop = child.getTop() + yvel * HIDE_FRICTION;
        return Math.abs(newTop - mMaxOffset) / (float) mPeekHeight > HIDE_THRESHOLD;
    }

    @VisibleForTesting
    private View findScrollingChild(View view) {
        if (ViewCompat.isNestedScrollingEnabled(view)) {
            return view;
        }
        if (view instanceof ViewPager) {
            ViewPager viewPager = (ViewPager) view;
            View currentViewPagerChild = ViewPagerUtils.getCurrentView(viewPager);
            if (currentViewPagerChild == null) {
                return null;
            }

            View scrollingChild = findScrollingChild(currentViewPagerChild);
            if (scrollingChild != null) {
                return scrollingChild;
            }
        } else if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0, count = group.getChildCount(); i < count; i++) {
                View scrollingChild = findScrollingChild(group.getChildAt(i));
                if (scrollingChild != null) {
                    return scrollingChild;
                }
            }
        }
        return null;
    }

    private float getYVelocity() {
        mVelocityTracker.computeCurrentVelocity(1000, mMaximumVelocity);
        return mVelocityTracker.getYVelocity(mActivePointerId);
    }

    void startSettlingAnimation(View child, int state) {
        int top;
        if (state == STATE_COLLAPSED) {
            top = mMaxOffset;
        } else if (state == STATE_EXPANDED) {
            top = mMinOffset;
        } else if (mHideable && state == STATE_HIDDEN) {
            top = mParentHeight;
        } else {
            throw new IllegalArgumentException("Illegal state argument: " + state);
        }
        if (mViewDragHelper.smoothSlideViewTo(child, child.getLeft(), top)) {
            setStateInternal(STATE_SETTLING);
            ViewCompat.postOnAnimation(child, new SettleRunnable(child, state));
        } else {
            setStateInternal(state);
        }
    }

    private final ViewDragHelper.Callback mDragCallback = new ViewDragHelper.Callback() {

        @Override
        public boolean tryCaptureView(View child, int pointerId) {
            if (mState == STATE_DRAGGING) {
                return false;
            }
            if (mTouchingScrollingChild) {
                return false;
            }
            if (mState == STATE_EXPANDED && mActivePointerId == pointerId) {
                View scroll = mNestedScrollingChildRef.get();
                if (scroll != null && scroll.canScrollVertically(-1)) {
                    // Let the content scroll up
                    return false;
                }
            }
            return mViewRef != null && mViewRef.get() == child;
        }

        @Override
        public void onViewPositionChanged(View changedView, int left, int top, int dx, int dy) {
            dispatchOnSlide(top);
        }

        @Override
        public void onViewDragStateChanged(int state) {
            if (state == ViewDragHelper.STATE_DRAGGING) {
                setStateInternal(STATE_DRAGGING);
            }
        }

        @Override
        public void onViewReleased(View releasedChild, float xvel, float yvel) {
            int top;
            @State int targetState;
            if (yvel < 0) { // Moving up
                top = mMinOffset;
                targetState = STATE_EXPANDED;
            } else if (mHideable && shouldHide(releasedChild, yvel)) {
                top = mParentHeight;
                targetState = STATE_HIDDEN;
            } else if (yvel == 0.f) {
                int currentTop = releasedChild.getTop();
                if (Math.abs(currentTop - mMinOffset) < Math.abs(currentTop - mMaxOffset)) {
                    top = mMinOffset;
                    targetState = STATE_EXPANDED;
                } else {
                    top = mMaxOffset;
                    targetState = STATE_COLLAPSED;
                }
            } else {
                top = mMaxOffset;
                targetState = STATE_COLLAPSED;
            }
            if (mViewDragHelper.settleCapturedViewAt(releasedChild.getLeft(), top)) {
                setStateInternal(STATE_SETTLING);
                ViewCompat.postOnAnimation(releasedChild,
                        new SettleRunnable(releasedChild, targetState));
            } else {
                setStateInternal(targetState);
            }
        }

        @Override
        public int clampViewPositionVertical(View child, int top, int dy) {
            return MathUtils.clamp(top, mMinOffset, mHideable ? mParentHeight : mMaxOffset);
        }

        @Override
        public int clampViewPositionHorizontal(View child, int left, int dx) {
            return child.getLeft();
        }

        @Override
        public int getViewVerticalDragRange(View child) {
            if (mHideable) {
                return mParentHeight - mMinOffset;
            } else {
                return mMaxOffset - mMinOffset;
            }
        }
    };

    void dispatchOnSlide(int top) {
        View bottomSheet = mViewRef.get();
        if (bottomSheet != null && mCallback != null) {
            if (top > mMaxOffset) {
                mCallback.onSlide(bottomSheet, (float) (mMaxOffset - top) /
                        (mParentHeight - mMaxOffset));
            } else {
                mCallback.onSlide(bottomSheet,
                        (float) (mMaxOffset - top) / ((mMaxOffset - mMinOffset)));
            }
        }
    }

    @VisibleForTesting
    int getPeekHeightMin() {
        return mPeekHeightMin;
    }

    private class SettleRunnable implements Runnable {

        private final View mView;

        @State
        private final int mTargetState;

        SettleRunnable(View view, @State int targetState) {
            mView = view;
            mTargetState = targetState;
        }

        @Override
        public void run() {
            if (mViewDragHelper != null && mViewDragHelper.continueSettling(true)) {
                ViewCompat.postOnAnimation(mView, this);
            } else {
                setStateInternal(mTargetState);
            }
        }
    }

    protected static class SavedState extends AbsSavedState {
        @State
        final int state;

        public SavedState(Parcel source) {
            this(source, null);
        }

        public SavedState(Parcel source, ClassLoader loader) {
            super(source, loader);
            //noinspection ResourceType
            state = source.readInt();
        }

        public SavedState(Parcelable superState, @State int state) {
            super(superState);
            this.state = state;
        }

        @Override
        public void writeToParcel(Parcel out, int flags) {
            super.writeToParcel(out, flags);
            out.writeInt(state);
        }

        public static final Creator<SavedState> CREATOR = new ClassLoaderCreator<SavedState>() {
            @Override
            public SavedState createFromParcel(Parcel in, ClassLoader loader) {
                return new SavedState(in, loader);
            }

            @Override
            public SavedState createFromParcel(Parcel in) {
                return new SavedState(in, null);
            }

            @Override
            public SavedState[] newArray(int size) {
                return new SavedState[size];
            }
        };
    }

    /**
     * A utility function to get the {@link ViewPagerBottomSheetBehavior} associated with the {@code view}.
     *
     * @param view The {@link View} with {@link ViewPagerBottomSheetBehavior}.
     * @return The {@link ViewPagerBottomSheetBehavior} associated with the {@code view}.
     */
    @SuppressWarnings("unchecked")
    public static <V extends View> ViewPagerBottomSheetBehavior<V> from(V view) {
        ViewGroup.LayoutParams params = view.getLayoutParams();
        if (!(params instanceof CoordinatorLayout.LayoutParams)) {
            throw new IllegalArgumentException("The view is not a child of CoordinatorLayout");
        }
        CoordinatorLayout.Behavior behavior = ((CoordinatorLayout.LayoutParams) params)
                .getBehavior();
        if (!(behavior instanceof ViewPagerBottomSheetBehavior)) {
            throw new IllegalArgumentException(
                    "The view is not associated with ViewPagerBottomSheetBehavior");
        }
        return (ViewPagerBottomSheetBehavior<V>) behavior;
    }
}
```

```java
public class ViewPagerUtils {
    public static View getCurrentView(ViewPager viewPager) {
        final int currentItem = viewPager.getCurrentItem();
        for (int i = 0; i < viewPager.getChildCount(); i++) {
            final View child = viewPager.getChildAt(i);
            final ViewPager.LayoutParams layoutParams = (ViewPager.LayoutParams) child.getLayoutParams();
            try {
                Field field = layoutParams.getClass().getDeclaredField("position");
                field.setAccessible(true);
                int position = field.getInt(layoutParams);
                if (!layoutParams.isDecor && currentItem == position) {
                    return child;
                }
            } catch (NoSuchFieldException e) {
                e.printStackTrace();
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }
        }
        return null;
    }
}
```

```java
public final class BottomSheetUtils {

    public static void setupViewPager(ViewPager viewPager) {
        final View bottomSheetParent = findBottomSheetParent(viewPager);
        if (bottomSheetParent != null) {
            viewPager.addOnPageChangeListener(new BottomSheetViewPagerListener(viewPager, bottomSheetParent));
        }
    }

    private static class BottomSheetViewPagerListener extends ViewPager.SimpleOnPageChangeListener {
        private final ViewPager viewPager;
        private final ViewPagerBottomSheetBehavior<View> behavior;

        private BottomSheetViewPagerListener(ViewPager viewPager, View bottomSheetParent) {
            this.viewPager = viewPager;
            this.behavior = ViewPagerBottomSheetBehavior.from(bottomSheetParent);
        }

        @Override
        public void onPageSelected(int position) {
            viewPager.post(new Runnable() {
                @Override
                public void run() {
                    behavior.invalidateScrollingChild();
                }
            });
        }
    }

    private static View findBottomSheetParent(final View view) {
        View current = view;
        while (current != null) {
            final ViewGroup.LayoutParams params = current.getLayoutParams();
            if (params instanceof CoordinatorLayout.LayoutParams && ((CoordinatorLayout.LayoutParams) params).getBehavior() instanceof ViewPagerBottomSheetBehavior) {
                return current;
            }
            final ViewParent parent = current.getParent();
            current = parent == null || !(parent instanceof View) ? null : (View) parent;
        }
        return null;
    }
}
```

```xml
<!-- design_view_pager_bottom_sheet_dialog.xml -->
<?xml version="1.0" encoding="utf-8"?>
<!--
  ~ Copyright (C) 2015 The Android Open Source Project
  ~
  ~ Licensed under the Apache License, Version 2.0 (the "License");
  ~ you may not use this file except in compliance with the License.
  ~ You may obtain a copy of the License at
  ~
  ~      http://www.apache.org/licenses/LICENSE-2.0
  ~
  ~ Unless required by applicable law or agreed to in writing, software
  ~ distributed under the License is distributed on an "AS IS" BASIS,
  ~ WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  ~ See the License for the specific language governing permissions and
  ~ limitations under the License.
-->
<androidx.coordinatorlayout.widget.CoordinatorLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <View
        android:id="@+id/touch_outside"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:soundEffectsEnabled="false"/>

    <FrameLayout
        android:id="@+id/design_bottom_sheet"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_gravity="center_horizontal|top"
        android:clickable="true"
        app:layout_behavior=".behavior.ViewPagerBottomSheetBehavior"
        style="?attr/bottomSheetStyle"/>

</androidx.coordinatorlayout.widget.CoordinatorLayout>
```

然后基于上述文件自定义BottomSheetDialog `ViewPagerBottomSheetDialog.java`以及`ViewPagerBottomSheetDialogFragment.java`

```java
public class ViewPagerBottomSheetDialog extends AppCompatDialog {

    private ViewPagerBottomSheetBehavior<FrameLayout> mBehavior;

    private boolean mCancelable = true;
    private boolean mCanceledOnTouchOutside = true;
    private boolean mCanceledOnTouchOutsideSet;
    private boolean mCreated;
    // 在这个自定义的Dialog中加入了设置高度的功能
    private int mPeekHeight;
    private int mMaxHeight;

    private Window mWindow;
    private ViewPagerBottomSheetBehavior mBottomSheetBehavior;

    public ViewPagerBottomSheetDialog(@NonNull Context context) {
        super(context, getThemeResId(context, 0));
        init(1000,1000); //
    }

    public ViewPagerBottomSheetDialog(@NonNull Context context, @StyleRes int theme) {
        super(context, getThemeResId(context, theme));
        // We hide the title bar for any style configuration. Otherwise, there will be a gap
        // above the bottom sheet when it is expanded.
        supportRequestWindowFeature(Window.FEATURE_NO_TITLE);
        init(1000, 1000);
    }

    public ViewPagerBottomSheetDialog(@NonNull Context context, int peekHeight, int maxHeight) {
        this(context, 0, peekHeight, maxHeight);
        init(peekHeight, maxHeight);
    }

    public ViewPagerBottomSheetDialog(@NonNull Context context, @StyleRes int theme, int peekHeight, int maxHeight) {
        super(context, getThemeResId(context, theme));
        // We hide the title bar for any style configuration. Otherwise, there will be a gap
        // above the bottom sheet when it is expanded.
        supportRequestWindowFeature(Window.FEATURE_NO_TITLE);
        init(peekHeight, maxHeight);
    }

    protected ViewPagerBottomSheetDialog(@NonNull Context context, boolean cancelable,
                                         DialogInterface.OnCancelListener cancelListener, int peekHeight, int maxHeight) {
        super(context, cancelable, cancelListener);
        supportRequestWindowFeature(Window.FEATURE_NO_TITLE);
        mCancelable = cancelable;
        init(peekHeight, maxHeight);
    }

    private void init(int peekHeight, int maxHeight) {
        mWindow = getWindow();
        mPeekHeight = peekHeight;
        mMaxHeight = maxHeight;
    }

    @Override
    public void setContentView(@LayoutRes int layoutResId) {
        super.setContentView(wrapInBottomSheet(layoutResId, null, null));
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setLayout(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);
        setPeekHeight();
        setMaxHeight();
        mCreated = true;
    }

    public void setPeekHeight(int peekHeight) {
        mPeekHeight = peekHeight;

        if (mCreated) {
            setPeekHeight();
        }
    }

    public void setMaxHeight(int height) {
        mMaxHeight = height;

        if (mCreated) {
            setMaxHeight();
        }
    }

    private void setPeekHeight() {
        if (mPeekHeight <= 0) {
            return;
        }

        if (getBottomSheetBehavior() != null) {
            mBottomSheetBehavior.setPeekHeight(mPeekHeight);
        }
    }

    private void setMaxHeight() {
        if (mMaxHeight <= 0) {
            return;
        }
        // 设置高度的核心函数
        mWindow.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, mMaxHeight);
        mWindow.setGravity(Gravity.BOTTOM);
    }

    private ViewPagerBottomSheetBehavior getBottomSheetBehavior() {
        if (mBottomSheetBehavior != null) {
            return mBottomSheetBehavior;
        }

        View view = mWindow.findViewById(R.id.design_bottom_sheet);
        // setContentView() 没有调用
        if (view == null) {
            return null;
        }
        mBottomSheetBehavior = ViewPagerBottomSheetBehavior.from(view);
        return mBottomSheetBehavior;
    }

    @Override
    public void setContentView(View view) {
        super.setContentView(wrapInBottomSheet(0, view, null));
    }

    @Override
    public void setContentView(View view, ViewGroup.LayoutParams params) {
        super.setContentView(wrapInBottomSheet(0, view, params));
    }

    @Override
    public void setCancelable(boolean cancelable) {
        super.setCancelable(cancelable);
        if (mCancelable != cancelable) {
            mCancelable = cancelable;
            if (mBehavior != null) {
                mBehavior.setHideable(cancelable);
            }
        }
    }

    @Override
    public void setCanceledOnTouchOutside(boolean cancel) {
        super.setCanceledOnTouchOutside(cancel);
        if (cancel && !mCancelable) {
            mCancelable = true;
        }
        mCanceledOnTouchOutside = cancel;
        mCanceledOnTouchOutsideSet = true;
    }

    private View wrapInBottomSheet(int layoutResId, View view, ViewGroup.LayoutParams params) {
        final CoordinatorLayout coordinator = (CoordinatorLayout) View.inflate(getContext(),
                R.layout.design_view_pager_bottom_sheet_dialog, null);
        if (layoutResId != 0 && view == null) {
            view = getLayoutInflater().inflate(layoutResId, coordinator, false);
        }
        FrameLayout bottomSheet = (FrameLayout) coordinator.findViewById(R.id.design_bottom_sheet);
        mBehavior = ViewPagerBottomSheetBehavior.from(bottomSheet);
        mBehavior.setBottomSheetCallback(mBottomSheetCallback);
        mBehavior.setHideable(mCancelable);
        if (params == null) {
            bottomSheet.addView(view);
        } else {
            bottomSheet.addView(view, params);
        }
        // We treat the CoordinatorLayout as outside the dialog though it is technically inside
        coordinator.findViewById(R.id.touch_outside).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (mCancelable && isShowing() && shouldWindowCloseOnTouchOutside()) {
                    cancel();
                }
            }
        });
        return coordinator;
    }

    private boolean shouldWindowCloseOnTouchOutside() {
        if (!mCanceledOnTouchOutsideSet) {
            if (Build.VERSION.SDK_INT < 11) {
                mCanceledOnTouchOutside = true;
            } else {
                TypedArray a = getContext().obtainStyledAttributes(
                        new int[]{android.R.attr.windowCloseOnTouchOutside});
                mCanceledOnTouchOutside = a.getBoolean(0, true);
                a.recycle();
            }
            mCanceledOnTouchOutsideSet = true;
        }
        return mCanceledOnTouchOutside;
    }

    private static int getThemeResId(Context context, int themeId) {
        if (themeId == 0) {
            // If the provided theme is 0, then retrieve the dialogTheme from our theme
            TypedValue outValue = new TypedValue();
            if (context.getTheme().resolveAttribute(
                    R.attr.bottomSheetDialogTheme, outValue, true)) {
                themeId = outValue.resourceId;
            } else {
                // bottomSheetDialogTheme is not provided; we default to our light theme
                themeId = R.style.Theme_Design_Light_BottomSheetDialog;
            }
        }
        return themeId;
    }

    private ViewPagerBottomSheetBehavior.BottomSheetCallback mBottomSheetCallback
            = new ViewPagerBottomSheetBehavior.BottomSheetCallback() {
        @Override
        public void onStateChanged(@NonNull View bottomSheet,
                                   @ViewPagerBottomSheetBehavior.State int newState) {
            if (newState == ViewPagerBottomSheetBehavior.STATE_HIDDEN) {
                dismiss();
            }
        }

        @Override
        public void onSlide(@NonNull View bottomSheet, float slideOffset) {
        }
    };
}
```

```java
public class ViewPagerBottomSheetDialogFragment extends AppCompatDialogFragment {

    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        return new ViewPagerBottomSheetDialog(getContext(), getTheme());
    }
}
```

在Activity中使用

```java
public class FourthActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_fourth);
        List<EmojiItem> data = new ArrayList<>();
        String[] arr = new String[]{
                "\uD83D\uDC4D", "❤️", "\uD83C\uDF89", "\uD83D\uDE02", "\uD83D\uDC4F", "\uD83D\uDE0E"
        };
        for (int i = 0; i < arr.length; i++) {
            data.add(new EmojiItem(arr[i], i + 10, null));
        }
        // 多了setMaxHeight(1600)和setPeekHeight(1000)
        findViewById(R.id.button4).setOnClickListener(v ->
                ListBottomSheetDialog.builder(FourthActivity.this)
                        .setEmojiItemList(data)
                        .setMaxHeight(1600)
                        .setPeekHeight(1000)
                        .setOffscreenPageLimit(5)
                        .setEnableScroll(true)
                        .show(getSupportFragmentManager()));
    }
}
```

结果如下，但是如果BottomSheetDialog官方将这个bug修复了，那么就不需要修改这么多的文件，而且自定义的ViewPagerBottomSheetBehavior只是复制了BottomSheetBehavior中的部分代码，可能存在其他问题尚未发现。

{% asset_img design5.gif %}


