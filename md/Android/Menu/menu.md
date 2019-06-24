参考：

> [菜单](https://developer.android.com/guide/topics/ui/menus)
> [Menu api](https://developer.android.com/reference/android/view/Menu)
> [图解 Android 事件分发机制](https://www.jianshu.com/p/e99b5e8bd67b)
> [Android事件分发机制 详解攻略](https://blog.csdn.net/carson_ho/article/details/54136311)
> [Activity、View、Window的理解一篇文章就够了](https://juejin.im/entry/596329686fb9a06bc903b6fd)

Menu，不同于Button、TextView之类的控件，它不需要在布局文件中指定位置，它是用于提供给用户额外的操作选择，因此不必局限于某一个固定位置，它可以搭配任何控件。

常见的Menu可以分为三种：
1. ToolBar上的选项菜单，这是固定的设计，配合ToolBar实现很简单；
2. 上下文菜单ContextMenu，与某一个控件关联，可以实现在点击（长按）的位置出现菜单选项的效果；
3. 弹出菜单PopupMenu，动态生成，作为一个点击事件触发，出现的位置与被点击的控件位置绑定（上方或下方），与上下文菜单不同。

{% asset_img 1.jpg %}

<!-- more -->

## 1. 菜单选项数据来源

如上图所示，展开的就是菜单Menu，菜单中包含一个一个的MenuItem，前面已经说了Menu不同于Button之类的控件，它的使用也是非常不同，最重要的部分其实是如何定义这些MenuItem，推荐的做法是使用`xml`资源文件定义MenuItem的文字内容以及Icon等等，然后在activity或fragment中处理点击事件；当然还有动态添加的方式可以使用。

### 1.1 使用xml定义菜单

这里先不必考虑如何使用Menu，只是定义菜单选项，需要在`res/menu/`目录下建一个`xml`文件

```xml
<!-- menu_main.xml -->
<menu xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">

    <item
        android:id="@+id/action_add_a_contact"
        android:icon="@drawable/ic_add_black_24dp"
        android:title="Add a Contact"
        app:showAsAction="always" />
    <item
        android:id="@+id/action_create_a_contact_group"
        android:icon="@drawable/ic_create_black_24dp"
        android:title="Create a Contact Group"
        app:showAsAction="never" />

    <item
        android:id="@+id/action_add_a_app"
        android:title="Add a App"
        app:showAsAction="always" />
    <item
        android:id="@+id/submenu"
        android:title="Submenu">

        <menu>
            <item
                android:id="@+id/action_create_a_channel"
                android:icon="@drawable/ic_create_new_folder_black_24dp"
                android:title="Create a Channel"
                app:showAsAction="never" />
            <item
                android:id="@+id/action_join_a_channel"
                android:icon="@drawable/ic_adjust_black_24dp"
                android:title="Join a Channel"
                app:showAsAction="never" />
        </menu>
    </item>

</menu>
```

上面的布局文件产生的效果如下图所示

{% asset_img 2.jpg %}

有几个特点：
1. 如果Item设置了Icon，那么如果出现在ToolBar上就是Icon，如果没有设置Icon，则显示大写文字；
2. Icon在折叠的Menu中不显示，但是在二级菜单中可以显示；
3. Item的顺序会被showAsAction参数影响。

### 1.2 在Activity中使用Menu

只需要在activity中重写`onCreateOptionsMenu()`方法即可，将上面定义的xml资源文件加载，前提是有ToolBar

```java
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        super.onCreateOptionsMenu(menu);
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }
```

点击事件处理，只需要在activity中重写`onOptionsItemSelected()`方法即可

```java
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case R.id.action_add_a_contact:
                Toast.makeText(this, "action_add_a_contact", Toast.LENGTH_SHORT).show();
                return true;
            case R.id.action_create_a_channel:
                Toast.makeText(this, "action_create_a_channel", Toast.LENGTH_SHORT).show();
                return true;
            case R.id.action_create_a_contact_group:
                Toast.makeText(this, "action_create_a_contact_group", Toast.LENGTH_SHORT).show();
                return true;
            case R.id.action_add_a_app:
                Toast.makeText(this, "action_add_a_app", Toast.LENGTH_SHORT).show();
                return true;
            case R.id.action_join_a_channel:
                Toast.makeText(this, "action_join_a_channel", Toast.LENGTH_SHORT).show();
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }
```

如果需要在运行时修改MenuItem的状态，可以重写`onPrepareOptionsMenu()`方法（每点击一次都会执行一次），比如可以在这里进行状态判断以禁用某些选项

```java
    // 首先需要一个flag控制
    private Boolean flag = false;

    // 其次在需要动态修改Menu状态的位置修改flag值，然后调用invalidateOptionsMenu()，
    // 这个方法会调用onPrepareOptionsMenu()方法，从而实现Menu的状态变化
    button.setOnClickListener(v -> {
        flag = true;
        invalidateOptionsMenu();  //  Android 3.0 及更高版本中必须调用invalidateOptionsMenu
    });

    @Override
    public boolean onPrepareOptionsMenu(Menu menu) {
        if (flag) {
            menu.findItem(R.id.action_create_a_contact_group).setVisible(false);
            menu.findItem(R.id.action_join_a_channel).setVisible(false);
        }
        return super.onPrepareOptionsMenu(menu);
    }
```

### 1.3 修改默认的ToolBar Menu图标以及点击背景色

默认为三个点，可以在`styles.xml`中进行修改

比如ToolBar在布局文件中如下

```xml
    <androidx.appcompat.widget.Toolbar
        android:id="@+id/my_toolbar"
        android:layout_width="match_parent"
        android:layout_height="?attr/actionBarSize"
        android:elevation="4dp"
        android:theme="@style/ToolbarBase"
        app:popupTheme="@style/OverflowMenu">

    </androidx.appcompat.widget.Toolbar>
```

两个参数
* theme：为整个ToolBar的主题，actionOverflowButtonStyle可以修改默认图标
* popupTheme：为弹出的Menu的主题，colorControlHighlight可以修改点击背景色

```xml
    <style name="ToolbarBase" parent="ThemeOverlay.AppCompat.ActionBar">
        <item name="actionOverflowButtonStyle">@style/OverflowButtonStyle</item>
        <!--<item name="actionOverflowMenuStyle">@style/OverflowMenu</item>-->
    </style>

    <style name="OverflowButtonStyle" parent="@android:style/Widget.ActionButton.Overflow">
        <item name="android:src">@drawable/ic_add_circle_outline_black_24dp</item>
        <item name="overlapAnchor">false</item>
    </style>

    <style name="OverflowMenu" parent="ThemeOverlay.AppCompat.Light">
        <!--遮挡属性-->
        <item name="overlapAnchor">false</item>
        <!--MenuItem选中背景颜色-->
        <item name="colorControlHighlight">@color/holo_blue_light</item>
    </style>
```

## 2. 上下文菜单

ContextMenu可以用在非常多的控件上，这里仅简单使用Button和RecyclerView，通常来说，触发ContextMenu的方式是长按，因此与该控件的OnLongClick事件冲突，
如果在onLongClick()方法中返回**true**，则代表点击事件被消耗，不再继续传递，那么ContextMenu不会触发；反之返回**false**，则ContextMenu被触发。由此可知，onLongClick()的优先级在ContextMenu之上，具体会在**Android事件传递中分析**。

ContextMenu可以在一个Activity中有多个，甚至可以在RecyclerView中使用，但是仅需要重写两个方法即可判断ContextMenu的来源。

{% asset_img 3.jpg %}

如上图所示，`Upload`后面跟的是该控件的`ItemId`，三个Menu各不相同，所以显然我们可以根据控件的不同生成不同的ContextMenu，点击事件同理。

使用ContextMenu的三个步骤：

1. 注册，更确切的说法是关联，即指定需要生成ContextMenu的控件，一句话解决

```java
        registerForContextMenu(recyclerView); // 对RecyclerView也是一样，但是这里我用的是自定义RecyclerView，稍后解释
        registerForContextMenu(button); // 直接在onCreate中注册即可，有几个控件就注册几次
        registerForContextMenu(button1);
```

2. 重写onCreateContextMenu方法，生成Menu

```java
    @Override
    public void onCreateContextMenu(ContextMenu menu, View v, ContextMenu.ContextMenuInfo menuInfo) {
        super.onCreateContextMenu(menu, v, menuInfo);
        // 这里实现了根据Id不同生成不同的Menu
        switch (v.getId()) {
            case R.id.first_button:
                addMenu(menu, v);
                break;
            case R.id.second_button:
                addMenu(menu, v);
                break;
            case R.id.recycler_view:
                addMenu(menu, v);
            default:
                break;
        }
    }

    private void addMenu(ContextMenu menu, View v) {
        menu.setHeaderTitle("Context Menu");
        menu.add(0, v.getId(), 0, "Upload" + v.getId());
        menu.add(0, v.getId(), 0, "Search");
        menu.add(1, v.getId(), 0, "Share");
        menu.add(1, v.getId(), 0, "Bookmark");
        // 同时可以通过groupId来禁用某些选项，这是额外的功能
        menu.setGroupEnabled(1, false);
    }
```

3. 重写onContextItemSelected方法，点击事件响应

```java
    @Override
    public boolean onContextItemSelected(MenuItem item) {
        // 这里需要注意，因为RecyclerView需要传入Item的Position属性，所以需要自定义RecyclerView
        RecyclerViewWithContextMenu.RecyclerViewContextInfo info = (RecyclerViewWithContextMenu.RecyclerViewContextInfo) item.getMenuInfo();
        Log.d(TAG, "onCreateContextMenu position = " + (info != null ? info.getPosition() : "-1"));
        // 通过判断点击的Item是否存在getMenuInfo获得的值，可以判断点击事件的来源，RecyclerView还是Button
        if (info != null && info.getPosition() != -1) {
            Toast.makeText(this, "Selected Item: " + item.getTitle() + " data: " + data.get(info.getPosition()), Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(this, "Selected Item: " + item.getTitle(), Toast.LENGTH_SHORT).show();
        }
        return true;
    }
```

**自定义的RecyclerViewWithContextMenu**

```java
public class RecyclerViewWithContextMenu extends RecyclerView {
    private static final String TAG = RecyclerViewWithContextMenu.class.getSimpleName();

    private RecyclerViewContextInfo mContextInfo = new RecyclerViewContextInfo();

    public RecyclerViewWithContextMenu(@NonNull Context context) {
        super(context);
    }

    public RecyclerViewWithContextMenu(@NonNull Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
    }

    public RecyclerViewWithContextMenu(@NonNull Context context, @Nullable AttributeSet attrs, int defStyle) {
        super(context, attrs, defStyle);
    }

    // 关键方法，重写showContextMenuForChild，将position属性传出去
    @Override
    public boolean showContextMenuForChild(View originalView) {
        final int longPressPosition = getChildAdapterPosition(originalView);
        if (longPressPosition >= 0) {
            mContextInfo.mPosition = longPressPosition;
            return super.showContextMenuForChild(originalView);
        }
        return false;
    }

    @Override
    protected ContextMenu.ContextMenuInfo getContextMenuInfo() {
        return mContextInfo;
    }

    // 通过自定义的ContextMenuInfo保存position的值，并提供调用的方法
    public static class RecyclerViewContextInfo implements ContextMenu.ContextMenuInfo {
        private int mPosition = -1;

        public int getPosition() {
            return mPosition;
        }
    }
}
```

## 3. 弹出菜单

PopupMenu是使用上最简单的，它的效果与ContextMenu类似但不完全相同，主要是位置是相对固定的，但是PopupMenu可以动态调用，与整体的布局无关

```java
public class MainActivity extends AppCompatActivity implements PopupMenu.OnMenuItemClickListener {

    private static final String TAG = MainActivity.class.getSimpleName();

    // ...

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        // ...
        // PopupMenu通过onClick事件创建
        findViewById(R.id.pop_button).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showPopupMenu(v);
            }
        });
        // ...
    }

    // ...

    public void showPopupMenu(View v) {
        // new一个对象，同样可以使用xml加载选项
        PopupMenu popup = new PopupMenu(this, v);
        popup.inflate(R.menu.menu_main);
        popup.show();
        // 这里需要继承PopupMenu.OnMenuItemClickListener接口
        popup.setOnMenuItemClickListener(this);
    }

    @Override
    public boolean onMenuItemClick(MenuItem item) {
        // 点击事件响应
        switch (item.getItemId()) {
            case R.id.action_add_a_contact:
                Toast.makeText(this, "action_add_a_contact", Toast.LENGTH_SHORT).show();
                return true;
            case R.id.action_create_a_channel:
                Toast.makeText(this, "action_create_a_channel", Toast.LENGTH_SHORT).show();
                return true;
            case R.id.action_create_a_contact_group:
                Toast.makeText(this, "action_create_a_contact_group", Toast.LENGTH_SHORT).show();
                return true;
            case R.id.action_add_a_app:
                Toast.makeText(this, "action_add_a_app", Toast.LENGTH_SHORT).show();
                return true;
            case R.id.action_join_a_channel:
                Toast.makeText(this, "action_join_a_channel", Toast.LENGTH_SHORT).show();
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }
}
```

## 4. Android事件分发机制

之所以会想到Android事件分发机制，主要是在ContextMenu的使用上发现长按事件的处理以及冲突，从而对长按事件优先级有一点思考，结合一些参考的文章，写一下自己的理解。

在使用ContextMenu中会产生以下几个问题，根据这些问题，可以尝试在源码里找结果。

* 为什么ContextMenu只需要注册就可以使用，而不是new一个对象出来，类似于PopupMenu？

首先看与ContextMenu相关的几个方法`registerForContextMenu`、`onCreateContextMenu`、`onContextItemSelected`

```java
// Activity.java registerForContextMenu这个方法仅仅是对view进行了注册listener

    /**
     * Registers a context menu to be shown for the given view (multiple views
     * can show the context menu). This method will set the
     * {@link OnCreateContextMenuListener} on the view to this activity, so
     * {@link #onCreateContextMenu(ContextMenu, View, ContextMenuInfo)} will be
     * called when it is time to show the context menu.
     *
     * @see #unregisterForContextMenu(View)
     * @param view The view that should show a context menu.
     */
    public void registerForContextMenu(View view) {
        view.setOnCreateContextMenuListener(this);
    }

// --------------------------------------------------------------------------------

// View.java 注册的过程中通过setLongClickable强制让此控件可以被long click，同时传递listener

    /**
     * Register a callback to be invoked when the context menu for this view is
     * being built. If this view is not long clickable, it becomes long clickable.
     *
     * @param l The callback that will run
     *
     */
    public void setOnCreateContextMenuListener(OnCreateContextMenuListener l) {
        if (!isLongClickable()) {
            setLongClickable(true);
        }
        getListenerInfo().mOnCreateContextMenuListener = l;
    }

    /**
        * Listener used to build the context menu.
        * This field should be made private, so it is hidden from the SDK.
        * {@hide}
        */
    protected OnCreateContextMenuListener mOnCreateContextMenuListener;

    // 这个listener的作用就是通过li.mOnCreateContextMenuListener.onCreateContextMenu(menu, this, menuInfo)
    // 将menu和menuInfo传出去，也就是说，我们在调用super.onCreateContextMenu(menu, v, menuInfo)后即可得到menu的实例，
    // 然后对menu实例进行处理，比如menu.add增加选项、menu.setGroupEnabled设置可点击的选项等等，
    // 此处暂不讨论createContextMenu是在哪里调用的，因为涉及到PhoneWindow和DecorView。

    /**
     * Show the context menu for this view. It is not safe to hold on to the
     * menu after returning from this method.
     *
     * You should normally not overload this method. Overload
     * {@link #onCreateContextMenu(ContextMenu)} or define an
     * {@link OnCreateContextMenuListener} to add items to the context menu.
     *
     * @param menu The context menu to populate
     */
    public void createContextMenu(ContextMenu menu) {
        ContextMenuInfo menuInfo = getContextMenuInfo();

        // Sets the current menu info so all items added to menu will have
        // my extra info set.
        ((MenuBuilder)menu).setCurrentMenuInfo(menuInfo);

        onCreateContextMenu(menu);
        ListenerInfo li = mListenerInfo;
        if (li != null && li.mOnCreateContextMenuListener != null) {
            li.mOnCreateContextMenuListener.onCreateContextMenu(menu, this, menuInfo);
        }

        // Clear the extra information so subsequent items that aren't mine don't
        // have my extra info.
        ((MenuBuilder)menu).setCurrentMenuInfo(null);

        if (mParent != null) {
            mParent.createContextMenu(menu);
        }
    }    

// --------------------------------------------------------------------------------

// Activity.java Item点击事件响应，除了ContextMenu，可以发现普通的ToolBar上的Menu的点击（onOptionsItemSelected）
// 也是在这里响应的。

    /**
     * Default implementation of
     * {@link android.view.Window.Callback#onMenuItemSelected}
     * for activities.  This calls through to the new
     * {@link #onOptionsItemSelected} method for the
     * {@link android.view.Window#FEATURE_OPTIONS_PANEL}
     * panel, so that subclasses of
     * Activity don't need to deal with feature codes.
     */
    public boolean onMenuItemSelected(int featureId, MenuItem item) {
        CharSequence titleCondensed = item.getTitleCondensed();
        // 通过featureId参数判断是来自ToolBar的Menu还是ContextMenu，显然这个参数来自于onMenuItemSelected方法被调用的地方
        // 可以在ToolbarWidgetWrapper.java和PhoneWindow.java中找到
        switch (featureId) {
            case Window.FEATURE_OPTIONS_PANEL:
                // Put event logging here so it gets called even if subclass
                // doesn't call through to superclass's implmeentation of each
                // of these methods below
                if(titleCondensed != null) {
                    EventLog.writeEvent(50000, 0, titleCondensed.toString());
                }
                // 在这里可以看到如果onOptionsItemSelected返回false，点击事件会继续传递下去，所以我们在重写onOptionsItemSelected
                // 方法时会在执行对应选项的点击事件后返回true以消耗点击事件
                if (onOptionsItemSelected(item)) {
                    return true;
                }
                if (mFragments.dispatchOptionsItemSelected(item)) {
                    return true;
                }
                if (item.getItemId() == android.R.id.home && mActionBar != null &&
                        (mActionBar.getDisplayOptions() & ActionBar.DISPLAY_HOME_AS_UP) != 0) {
                    if (mParent == null) {
                        return onNavigateUp();
                    } else {
                        return mParent.onNavigateUpFromChild(this);
                    }
                }
                return false;

            case Window.FEATURE_CONTEXT_MENU:
                if(titleCondensed != null) {
                    EventLog.writeEvent(50000, 1, titleCondensed.toString());
                }
                // 同上
                if (onContextItemSelected(item)) {
                    return true;
                }
                return mFragments.dispatchContextItemSelected(item);

            default:
                return false;
        }
    }
```

综上所述，ContextMenu其实是一个比较深层次的控件，它的创建过程被更复杂的PhoneWindow以及DecorView等控制，对开发者来说，Menu是一个直接使用就行的控件，底层不希望开发者对Menu进行指定布局选项之外的操作，因此我们不需要new一个对象出来。至于它是如何在PhoneWindow以及DecorView中创建的，我可能在接下来的博客中写一下自己的理解。

* ContextMenu的触发与该控件的onLongClick方法的冲突是如何产生的？

在上面ContextMenu的使用过程中，会发现ContextMenu默认是长按触发，而且源码里也说明了，控件会被强制赋予长按属性，那么如果同时设置该控件的onLongClick方法会产生怎样的效果，代码很简单，这里有一个疑问了，为什么要返回true？如果返回false会怎样？为什么onClick方法不用返回值？

```java
       button.setOnLongClickListener(new View.OnLongClickListener() {
           @Override
           public boolean onLongClick(View v) {
               Toast.makeText(MainActivity.this, "button long click", Toast.LENGTH_SHORT).show();
               return true;
           }
       });
```

结果也是很明显的，测试以下就知道这里返回true，那么button的ContextMenu无法触发，Toast会正常产生；返回false，那么button的Toast会产生，而且ContextMenu也会产生，onLongClick方法在onCreateContextMenu方法之前执行。

由此产生了另一个问题，onLongClick方法是如何产生的，解决了这个问题，那么所有的问题都将迎刃而解。

```java
// View.java 最直接的调用onLongClick方法的位置

    /**
     * Calls this view's OnLongClickListener, if it is defined. Invokes the
     * context menu if the OnLongClickListener did not consume the event,
     * optionally anchoring it to an (x,y) coordinate.
     *
     * @param x x coordinate of the anchoring touch event, or {@link Float#NaN}
     *          to disable anchoring
     * @param y y coordinate of the anchoring touch event, or {@link Float#NaN}
     *          to disable anchoring
     * @return {@code true} if one of the above receivers consumed the event,
     *         {@code false} otherwise
     */
    private boolean performLongClickInternal(float x, float y) {
        sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_LONG_CLICKED);

        boolean handled = false;
        final ListenerInfo li = mListenerInfo;
        if (li != null && li.mOnLongClickListener != null) {
            // listener调用onLongClick方法的位置，返回值为handled
            handled = li.mOnLongClickListener.onLongClick(View.this);
        }
        // 如果handled为true，则不会执行下面整个方法showContextMenu，看名字也知道这是ContextMenu显示的方法了，
        // 所以如果onLongClick返回true，则不会显示ContextMenu；反之同理。所以上面关于执行先后顺序的疑问解决了
        if (!handled) {
            final boolean isAnchored = !Float.isNaN(x) && !Float.isNaN(y);
            handled = isAnchored ? showContextMenu(x, y) : showContextMenu();
        }
        if ((mViewFlags & TOOLTIP) == TOOLTIP) {
            // 如果handled为true，则不会执行下面整个方法showLongClickTooltip，这个Tooltip是另一个控件，
            // 其触发也是与长按事件相关，暂且不表
            if (!handled) {
                handled = showLongClickTooltip((int) x, (int) y);
            }
        }
        if (handled) {
            performHapticFeedback(HapticFeedbackConstants.LONG_PRESS);
        }
        // 最后还是返回handled的值
        return handled;
    }

    // 再看看onClick方法的调用，很明显单击事件没有其他控件与其冲突，所以它的返回值为空
    /**
     * Call this view's OnClickListener, if it is defined.  Performs all normal
     * actions associated with clicking: reporting accessibility event, playing
     * a sound, etc.
     *
     * @return True there was an assigned OnClickListener that was called, false
     *         otherwise is returned.
     */
    // NOTE: other methods on View should not call this method directly, but performClickInternal()
    // instead, to guarantee that the autofill manager is notified when necessary (as subclasses
    // could extend this method without calling super.performClick()).
    public boolean performClick() {
        // We still need to call this method to handle the cases where performClick() was called
        // externally, instead of through performClickInternal()
        notifyAutofillManagerOnClick();

        final boolean result;
        final ListenerInfo li = mListenerInfo;
        if (li != null && li.mOnClickListener != null) {
            playSoundEffect(SoundEffectConstants.CLICK);
            // 无返回值，没有冲突，result直接设置为true即可
            li.mOnClickListener.onClick(this);
            result = true;
        } else {
            result = false;
        }

        sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_CLICKED);

        notifyEnterOrExitForAutoFillIfNeeded(true);

        return result;
    }


    // 然后就是点击事件与长按事件是如何产生的，这里牵涉到onTouchEvent方法，这里把无关代码略过，仅保留重要代码
    /**
     * Implement this method to handle touch screen motion events.
     * <p>
     * If this method is used to detect click actions, it is recommended that
     * the actions be performed by implementing and calling
     * {@link #performClick()}. This will ensure consistent system behavior,
     * including:
     * <ul>
     * <li>obeying click sound preferences
     * <li>dispatching OnClickListener calls
     * <li>handling {@link AccessibilityNodeInfo#ACTION_CLICK ACTION_CLICK} when
     * accessibility features are enabled
     * </ul>
     *
     * @param event The motion event.
     * @return True if the event was handled, false otherwise.
     */
    public boolean onTouchEvent(MotionEvent event) {

        // ... 

        if (clickable || (viewFlags & TOOLTIP) == TOOLTIP) {
            switch (action) {
                // MotionEvent分为四种ACTION_UP、ACTION_DOWN、ACTION_CANCEL、ACTION_MOVE
                // 分别对应手指在屏幕的状态：抬起、按下、（例外，暂且不解释）、滑动
                // 通过对这些MotionEvent的监听可以实现各种点击效果，比如多连击、定时点击等等效果，
                // 也可以控制事件的冲突，我们仅需要在自定义控件中重写onTouchEvent方法即可。
                case MotionEvent.ACTION_UP:
                    // ...
                    // 为什么要在抬起的时候触发点击事件performClick，因为长按与点击是有冲突的，
                    // 长按会在ACTION_DOWN里触发，这是由时间控制的，因此ACTION_UP中与长按事件其实关系就不大了
                    // 所以在这里处理点击事件是一个较为合理的设计
                    if ((mPrivateFlags & PFLAG_PRESSED) != 0 || prepressed) {
                        // take focus if we don't have it already and we should in
                        // touch mode.
                        boolean focusTaken = false;
                        if (isFocusable() && isFocusableInTouchMode() && !isFocused()) {
                            focusTaken = requestFocus();
                        }

                        if (prepressed) {
                            // The button is being released before we actually
                            // showed it as pressed.  Make it show the pressed
                            // state now (before scheduling the click) to ensure
                            // the user sees it.
                            setPressed(true, x, y);
                        }

                        if (!mHasPerformedLongPress && !mIgnoreNextUpEvent) {
                            // This is a tap, so remove the longpress check
                            removeLongPressCallback();

                            // Only perform take click actions if we were in the pressed state
                            if (!focusTaken) {
                                // Use a Runnable and post this rather than calling
                                // performClick directly. This lets other visual state
                                // of the view update before click actions start.
                                if (mPerformClick == null) {
                                    // 点击事件的关键，这里的PerformClick是一个Runnable，为什么要用Runnable，之后再解释
                                    mPerformClick = new PerformClick();
                                }
                                // 通过handler调用performClick方法，点击事件就完成了
                                if (!post(mPerformClick)) {
                                    performClickInternal();
                                }
                            }
                        }
                        // ...
                    }
                    mIgnoreNextUpEvent = false;
                    break;

                case MotionEvent.ACTION_DOWN:
                    if (event.getSource() == InputDevice.SOURCE_TOUCHSCREEN) {
                        mPrivateFlags3 |= PFLAG3_FINGER_DOWN;
                    }
                    // mHasPerformedLongPress用于解决长按与点击的事件冲突，具体可以看源码
                    mHasPerformedLongPress = false;

                    // clickable表示该控件是否可以点击（包括点击、长按等）
                    if (!clickable) {
                        // 如果控件不可点击，那么会判断是否需要显示Tooltip或者什么都不干，然后break，
                        // 具体可以看checkForLongClick方法
                        checkForLongClick(0, x, y);
                        break;
                    }

                    // performButtonActionOnTouchDown与外设有关，暂时不用考虑
                    if (performButtonActionOnTouchDown(event)) {
                        break;
                    }

                    // Walk up the hierarchy to determine if we're inside a scrolling container.
                    boolean isInScrollingContainer = isInScrollingContainer();

                    // For views inside a scrolling container, delay the pressed feedback for
                    // a short period in case this is a scroll.
                    // 该控件在一个可以滑动的container内，则会增加一个反应延时，但是最终都是调用checkForLongClick
                    if (isInScrollingContainer) {
                        mPrivateFlags |= PFLAG_PREPRESSED;
                        if (mPendingCheckForTap == null) {
                            mPendingCheckForTap = new CheckForTap();
                        }
                        mPendingCheckForTap.x = event.getX();
                        mPendingCheckForTap.y = event.getY();
                        postDelayed(mPendingCheckForTap, ViewConfiguration.getTapTimeout());
                    } else {
                        // Not inside a scrolling container, so show the feedback right away
                        setPressed(true, x, y);
                        // checkForLongClick也是一个Runnable，最终调用还是performLongClickInternal
                        checkForLongClick(0, x, y);
                    }
                    break;

                // ACTION_CANCEL状态比较难触发，举个例子，在MIUI中开启“传送门”功能，就可以触发
                case MotionEvent.ACTION_CANCEL:
                    if (clickable) {
                        setPressed(false);
                    }
                    removeTapCallback();
                    removeLongPressCallback();
                    mInContextButtonPress = false;
                    mHasPerformedLongPress = false;
                    mIgnoreNextUpEvent = false;
                    mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
                    break;

                // ACTION_MOVE状态下removeTapCallback方法和removeLongPressCallback可以取消点击事件，
                // 这也就是为什么我们在按住某个按钮然后滑动出去就可以避免触发点击事件
                case MotionEvent.ACTION_MOVE:
                    if (clickable) {
                        drawableHotspotChanged(x, y);
                    }

                    // Be lenient about moving outside of buttons
                    if (!pointInView(x, y, mTouchSlop)) {
                        // Outside button
                        // Remove any future long press/tap checks
                        removeTapCallback();
                        removeLongPressCallback();
                        if ((mPrivateFlags & PFLAG_PRESSED) != 0) {
                            setPressed(false);
                        }
                        mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
                    }
                    break;
            }

            return true;
        }

        return false;
    }
```

根据上述源码，我们知道了ContextMenu与长按事件冲突的原因，点击事件与长按事件是如何产生的，但是随之而来有了新的问题。

* 为什么要使用Runnable来调用以及如果父容器有点击事件的同时子控件也有点击事件，那么事件传递的过程以及中间冲突是如何解决的？

```java
// View.java 从源码中可以看到，这是一个专门用于UI线程的Handler，通过这个Handler发送的Runnable都会在UI线程中运行
    /**
     * <p>Causes the Runnable to be added to the message queue.
     * The runnable will be run on the user interface thread.</p>
     *
     * @param action The Runnable that will be executed.
     *
     * @return Returns true if the Runnable was successfully placed in to the
     *         message queue.  Returns false on failure, usually because the
     *         looper processing the message queue is exiting.
     *
     * @see #postDelayed
     * @see #removeCallbacks
     */
    public boolean post(Runnable action) {
        final AttachInfo attachInfo = mAttachInfo;
        if (attachInfo != null) {
            return attachInfo.mHandler.post(action);
        }

        // Postpone the runnable until we know on which thread it needs to run.
        // Assume that the runnable will be successfully placed after attach.
        getRunQueue().post(action);
        return true;
    }
```

结合上面的部分注释，说明一个原理，所有的点击事件以及屏幕绘制都要在UI线程中处理，这是为了方便点击触发时重绘UI

```java
// Use a Runnable and post this rather than calling
// performClick directly. This lets other visual state
// of the view update before click actions start.
```














