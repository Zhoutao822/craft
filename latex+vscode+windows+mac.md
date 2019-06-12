# VSCode搭建LaTeX论文写作环境

参考：

[中国科学技术大学学位论文 LaTeX 模板](https://github.com/ustctug/ustcthesis)

[论文写作的又一利器：VSCode + LaTeX Workshop + MikTex + Git](https://blog.csdn.net/yinqingwang/article/details/79684419)

[MikTeX](https://miktex.org/)

[MacTeX](https://www.tug.org/mactex/)

[VSCode](https://code.visualstudio.com/)

## Windows环境

### 1. 安装LaTeX发行版

在Windows下我选择的是MikTeX，Mac下选择的是MacTex，这个LaTeX发行版相当于一个开发工具包，你需要的编译器以及某些资源文件都包含在这个包里面，安装完成后可以通过命令行启用。

在Windows下MikTeX的安装教程链接为[Install MiKTeX on Windows](https://miktex.org/howto/install-miktex)，链接里也给出了安装包的地址[Basic MiKTeX Installer](https://miktex.org/download)，安装完成后打开 MiKTeX Console 更新package。目前这个阶段还不需要安装额外的package，这个我们可以等到编译论文的时候再下载。

### 2. VSCode安装与参数设置

VSCode的安装没什么可说的，完成后需要在**扩展**中搜索`latex`，就可以找到需要的插件`LaTeX Workshop`，安装完成后需要配置一些参数，在设置中搜索`latex`，打开`settings.json`，加入以下参数

{% asset_img latex-workshop.png %}

```json
"latex-workshop.view.pdf.viewer": "tab",
"latex-workshop.latex.recipes": [
    {
        "name": "latexmk",
        "tools": [
            "latexmk"
        ]
    },
    {
        "name": "pdflatex",
        "tools": [
            "pdflatex"
        ]
    },
    {
        "name": "pdflatex -> bibtex -> pdflatex*2",
        "tools": [
            "pdflatex",
            "bibtex",
            "pdflatex",
            "pdflatex"
        ]
    }
],
"latex-workshop.latex.tools": [
    {
        "name": "xelatex",
        "command": "xelatex",
        "args": [
            "-synctex=1",
            "-interaction=nonstopmode",
            "-file-line-error",
            "%DOC%"
        ]
    },
    {
        "name": "pdflatex",
        "command": "pdflatex",
        "args": [
            "-synctex=1",
            "-interaction=nonstopmode",
            "-file-line-error",
            "%DOC%"
        ]
    },
    {
        "name": "latexmk",
        "command": "latexmk",
        "args": [
            "-xelatex"
        ]
    },
    {
        "name": "bibtex",
        "command": "bibtex",
        "args": [
            "%DOCFILE%"
        ]
    }
],
"latex-workshop.latex.autoBuild.run": "never",
"latex-workshop.latex.autoClean.run": "never",
"latex-workshop.latex.clean.fileTypes": [
        "*.aux",
        "*.bbl",
        "*.blg",
        "*.idx",
        "*.ind",
        "*.lof",
        "*.lot",
        "*.out",
        "*.toc",
        "*.acn",
        "*.acr",
        "*.alg",
        "*.glg",
        "*.glo",
        "*.gls",
        "*.ist",
        "*.fls",
        "*.log",
        "*.xdv",
        "*.fdb_latexmk",
        "*.synctex.gz"
    ]
```

参数说明：

1. `latex-workshop.view.pdf.viewer`设置为`tab`可以在VSCode里查看生成的pdf文件，你也可以选择其他方式；
2. `latex-workshop.latex.tools`定义你可能需要用到的编译工具，比如`latexmk`、`xelatex`、`pdflatex`等等，这里定义的工具才可以在`latex-workshop.latex.recipes`里使用，**这里`latexmk`的参数被修改为`-xelatex`，与Github上相同**，我这里加入了很多的工具，并不一定全都要用；
3. `latex-workshop.latex.recipes`定义编译方式，比如`latexmk`、`pdflatex -> bibtex -> pdflatex*2`，这里同上，也并不一定全都要用，不同的编译方式会导致最终生成的pdf文件内容存在差异，使用`latexmk`以外的编译工具编译[中国科学技术大学学位论文 LaTeX 模板](https://github.com/ustctug/ustcthesis)可能会导致pdf中丢失目录以及文献列表等内容，在这里定义的编译方式会在后面显示在VSCode的选项中；
4. `latex-workshop.latex.autoBuild.run`设置为`never`是为了避免每次修改完`tex`文件后自动编译，也可以不设置此参数；
5. `latex-workshop.latex.autoClean.run`设置为`never`是为了避免自动清理编译过程产生的临时文件，这里会有一些log文件，也可以不设置此参数。
6. `latex-workshop.latex.clean.fileTypes`设置需要清理临时文件类型，以各种后缀表示，有些文件可能不需要清理，这个需要自行判断。

### 3. 编译论文模板

在[中国科学技术大学学位论文 LaTeX 模板](https://github.com/ustctug/ustcthesis)下载release文件[ustcthesis-v3.1.06.zip](https://github.com/ustctug/ustcthesis/releases/download/v3.1.06/ustcthesis-v3.1.06.zip)，这里面有模板以及样例文件。

文件目录大概如下图，里面某些pdf和tex文件可能不同，但不重要

{% asset_img ustcthesis.png %}

用VSCode打开模板文件，并打开`main.tex`文件，这里可以先把`main.pdf`重命名一下，此时如果之前的步骤都是对的，那么VSCode的左下角会有一个勾的图标，点击后应该如下图

{% asset_img recipe.png %}

这里会发现之前设置参数时加入的`recipe`都显示出来，中国科学技术大学学位论文 LaTeX 模板 需要用`latexmk`编译，所以直接双击`Recipe: latexmk`编译`main.tex`，生成`main.pdf`文件，在编译过程中会提示你缺少某些package，这些package里面有需要的一些样式文件，类似于CSS，弹出的窗口来自于`MikTeX Console`，点击确定下载即可，可能会需要点很多次，当所有需要的package下载完成后编译也可以继续下去，最后比对一下生成的`main.pdf`文件内容与重命名之前的`main.pdf`，看看有没有缺失或者显示不对的地方，如果有，再查找原因，一般来说问题出在缺少某些package。如果需要清理生成的临时文件只需要双击`Clean up`即可。

这是我生成的pdf文件截图，第一张图我修改为`硕士`，第二张图生成当前时间。

{% asset_img 1.png %}

{% asset_img 2.png %}

## Mac环境

### 1. 安装LaTeX发行版

在Mac下选择的安装MacTeX，而MacTeX有几个不同的安装包，一个是`MacTeX.pkg`，大概3.9G，还有一个是`BasicTeX.pkg`，大概76M，区别在于前者包括了GUI，大概有4个工具配合使用，后者没有GUI仅提供命令行工具，这里我选择了后者，前者应该也没有区别。

命令行工具为`tlmgr`，我在运行时需要加`sudo`，应该是安装路径对一般用户不可写。

然后需要使用`tlmgr`安装一些package，我们先设置一下镜像源加速下载

```shell
# 这是清华镜像源，也可以使用科大镜像源http://mirrors.ustc.edu.cn/CTAN/systems/texlive/tlnet
tlmgr option repository https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet
```

然后更新自己和所有的package

```shell
sudo tlmgr update --self --all
```

最后需要下载`latexmk`包，Windows不需要应该是MikTeX中已经包含了这个包，而Mac下`BasicTeX`没有包含，所以需要自己下载。

```shell
sudo tlmgr install latexmk
```

### 2. VSCode安装与参数设置

安装配置同Windows。

### 3. 编译论文模板

在Mac上使用`latexmk -xelatex main.tex`会失败，而且系统不会像Windows那样提示你需要下载哪些package，每次失败都会告诉你缺少哪个文件，这个在log中是可以看到的，一般来说在[CTAN官网](https://www.ctan.org/)搜索缺少的文件就可以知道需要下载哪个package。

下载package的代码为

```shell
# package_name为包名，比如可能有siunitx...
sudo tlmgr install package_name
```

这些下载的package是可以在`/usr/local/texlive/2019basic/texmf-dist/tex/latex`下找到的，我的可以正确运行科大LaTeX模板的package截图如下，不想一个一个搜索的可以直接对照下载缺少的package。

{% asset_img 3.png %}

最后同上测试一下能否正确生成pdf文件。
