# 华为云图引擎服务GES-实时推荐算法

## 1. GES服务说明

具体可以参考官网 [GES](https://console.huaweicloud.com/ges/?agencyId=13f4d646cf75479bbe4418ae72d7f446&region=cn-north-1&locale=zh-cn#/management/dashboard)，根据我的学习了解，GES提供了一种以图形化形式做数据分析的工具，也就是说，按照要求输入结构化数据，你可以在平台上看见数据之间是怎样联系的。本文就以实验中使用的点-边数据类型来进行分析。

## 2. 元数据分析

创建图的过程中需要提供三个文件，点数据`vertex.csv`，边数据`edge.csv`，映射模板`schema.xml`。

### 2.1 点数据

在GES服务中，我们使用面向对象的思想，对于需要进行分析的数据都抽象为一个对象，每个对象拥有各自的属性，不同种类对象的属性不同，在实验中给出的**电影喜好数据**中，点数据即对象，存在同一个`vertex.csv`文件中，我们可以看作有5个类，分别对应movie，user，genre，actor，director（虽然在GES中是以label表示）。

!(ges0.png)
!(ges1.png)
!(ges2.png)
!(ges3.png)
!(ges4.png)

每一条数据的第一列是id，第二列是label，剩下其他列是一些附加属性，在GES中，每一个id对应一个点（唯一），点与点之间通过边数据联系起来，label用于筛选我们的分析目标，比如我们需要分析某个人喜欢的电影，那么这个人对应一个点，在这个点包括的所有边中，按照label筛选出另一端点为电影的点，那么按照分数排序就可以得到用户最喜欢的某些电影了。

### 2.2 边数据

边数据主要描述点与点之间的关系，在`edge.csv`文件中，一共有like，friends，hasGener，hasActor，hasDirector五种。like对应user-movie，friends对应user-user，hasGener对应movie-gener，hasActor对应movie-actor，hasDirector对应movie-director。也就是说上面提到的根据某个用户喜欢某个电影来进行推荐，就是从一个点出发，找到所有边（label为movie），再加上一些其他的算法计算分数，就形成了最终推荐的结果。

!(ges5.png)
!(ges6.png)
!(ges7.png)
!(ges8.png)
!(ges9.png)

推荐结果如下

!(ges10.png)

### 2.3 映射模板

我们将不同类型的点数据都保存在同一csv文件中，因此需要用映射模板解析数据，解析的形式就是上面描述的按照label分类，不同label的数据包括不同的属性，属性有其各自的数据格式。

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<PMML version="3.0"
  xmlns="http://www.dmg.org/PMML-3-0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema_instance" >
  <labels>
    <label name="like">
	        <properties> 
            <property name="Datetime" cardinality="single" dataType="date"/>
        </properties>
    </label>
    <label name="friends">
    </label>
    <label name="hasActor">
    </label>
	<label name="hasDirector">
    </label>
	 <label name="hasGenre">
    </label>
    <label name="user">
	        <properties>
			<property name="ChineseName" cardinality="single" dataType="string" />
            <property name="Gender" cardinality="single" dataType="enum" typeNameCount="2" 
			typeName1="F" typeName2="M"/>
            <property name="Age" cardinality="single" dataType="enum" typeNameCount="7" 
			typeName1="Under 18" typeName2="18-24" typeName3="25-34" typeName4="35-44" typeName5="45-49"
			 typeName6="50-55" typeName7="56+"/> 
			<property name="Occupation" cardinality="single" dataType="string"/>
			<property name="Zip-code" cardinality="single" dataType="char array" maxDataSize="12"/>
        </properties>
    </label>
    <label name="movie">
	        <properties>
            <property name="ChineseTitle" cardinality="single" dataType="string"/>
			<property name="Year" cardinality="single" dataType="int"/> 
        </properties>
    </label>
    <label name="actor">
    </label>
    <label name="director">
    </label>
    <label name="genre">
    </label>
</labels>
</PMML>
```

## 3. 实时推荐算法分析

实时推荐算法（Real-time Recommendation）是一种基于随机游走模型的实时推荐算法，能够推荐与输入节点相近程度高、关系或喜好相近的节点。

参考：[实时推荐算法](https://support.huaweicloud.com/usermanual-ges/ges_01_0047.html)

### 3.1 参数

* sources：算法的起点，以id为数据类型
* label：边筛选条件，以label为数据类型
* directed：边的方向，为true时点与点之间为单向，反之双向，这个在edge.csv中很关键，比如friends关系中，单向就意味着算法搜索只能从A到B，不能从B到A，双向会产生循环，因此需要N参数
* N：总游走步数，避免走入循环
* np：推荐候选节点个数，若某个source节点的候选推荐节点达到“np”，对于该source节点的随机游走将提前结束
* nv：候选推荐节点所需访问次数的最小值，对于一个节点，如果其在随机游走过程被访问到，且被访问到的次数达到“nv”，则该节点将记入候选推荐的节点。
* alpha：权重系数, 其值越大步长越长

### 3.2 算法分析

1. 首先算法找到所有的sources节点，然后根据directed参数得到所有能通向的路径；
2. 每一个sources节点找到所有能前往的下一条路时，以1 / 路径数 的概率让其选择一条路，并前往下一个节点；
3. 当到达下一个节点时，该节点的被访问数加1，同时总游走步数N减1，然后按照2的规则随机到达下一个节点；
4. 若到达当前节点后，被访问数达到nv，则返回sources节点重新开始，同时将该节点加入候选节点中，若候选节点总数达到np，则停止搜索，按照label筛选返回结果；
5. 若np为1，则所有候选结果的分数差距不大；若np越大，则每个结果的分数差距变大，每个节点的分数由alpha和到达该节点需要的步数相关，步数越少分数越高，步长alpha越小，分数差异越大；
6. 最后由不同sources出发得到的所有候选节点的分数相加，然后输出按照分数大小排列好的结果。

实验验证猜想：

* 随机选择路径，因此参数相同时结果不一定相同

!(ges11.png)
!(ges12.png)

* np越大，预测结果分数差异越大，alpha越小，分数差异越大

!(ges13.png)
!(ges14.png)
!(ges15.png)
!(ges16.png)
!(ges17.png)

* sources越多，分数差异越大，预测结果越分明

!(ges18.png)
!(ges19.png)

* N越大，预测结果越多，分数差异越大

!(ges18.png)
!(ges20.png)

* 双向比单向能得到更多的预测结果

!(ges18.png)
!(ges21.png)



