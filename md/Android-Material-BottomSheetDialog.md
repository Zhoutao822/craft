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

## 2. 

