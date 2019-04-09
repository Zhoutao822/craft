## 1. 单选题
1. 下面这段程序的输出结果是

```java
public class Main {
    public static void main(String[] args) {
        split(12);
    }
    public static int split(int number) {
        if (number > 1) {
            if (number % 2 != 0) {
                System.out.print(split((number + 1) / 2));
            }
            System.out.print(split(number / 2));
        }
        return number;
    }
}
```

```
A. 63121    
B. 11236   
C. 12136   
D. 61213
```

2. 已知二叉树后序遍历序列是dabec，中序遍历序列是debac，它的前序遍历序列是

```
A. cedab   
B. cedba  
C. cebad   
D. cebda
```

3. 一棵具有n个结点的完全二叉树的树高度（深度）是

```
A. log2(n)+1  
B. [log2(n)]
C. [log2(n)]+1 
D. log2(n)-1
```

4. 下面这段程序的输出结果是

```java
class A {
    public A() {
        System.out.println("A的构造函数");
    }
    {
        System.out.println("A的构造代码块");
    }
    static {
        System.out.println("A的静态代码块");
    }
}
class B extends A {
    public B() {
        System.out.println("B的构造函数");
    }
    {
        System.out.println("B的构造代码块");
    }
    static {
        System.out.println("B的静态代码块");
    }
}
public class Solution{
    public static void main(String[] args) {
        A a = new A();
        B b = new B();
    }
}
```

```
A. A的静态代码块 A的构造代码块 A的构造函数 A的构造代码块 
A的构造函数 B的静态代码块 B的构造代码块 B的构造函数
B. A的静态代码块 A的构造函数 A的构造代码块 A的构造函数 
A的构造代码块 B的静态代码块 B的构造函数 B的构造代码块 
C. A的静态代码块 A的构造代码块 A的构造函数 B的静态代码块
A的构造代码块 A的构造函数 B的构造代码块 B的构造函数
D. A的静态代码块 A的构造代码块 A的构造函数 B的静态代码块 
B的构造代码块 B的构造函数
```

5. 下面这段程序的输出结果是

```java
public class Solution{
    public static void main(String[] args) {
        String a = new String("myString");
        String b = "myString";
        String c = "my" + "String";
        String d = c;
        System.out.print(a == b);
        System.out.print(a == c);
        System.out.print(b == c);
        System.out.print(b == d);
    }
}
```

```
A. falsefalsetruetrue 
B. truetruefalsefalse
C. falsetruetruefalse
D. falsetruefalsetrue
```

6. Service提供的回调方法中，哪一个方法在生命周期中可能被多次回调

```
A. onCreate
B. onStartCommand
C. onBind
D. onDestory
```

7. ⼀个完全⼆叉树中有330个叶子节点, 则在该⼆叉树中的节点个数为

```
A. 659
B. 660
C. 可能为659或者660
D. 不可能为659和660
```

8. 关于http请求里post和get描述不正确的是

```
A. POST请求的数据不会暴露在地址栏中
B. GET请求的URL中不能携带数据参数
C. 根据HTTP规范，POST表示可能修改变服务器上的资源的请求
D. 根据HTTP规范，GET用于信息获取，而且应该是安全的和幂等的
```

9. android提供的跨进程通讯方式不包括以下哪个

```
A. ContentProvider
B. BroadcastReceiver
C. AIDL
D. Handler
```

10. android的view控件从被创建到显示，不会经过以下哪个方法

```
A. onDraw
B. onMeasure
C. onAdd
D. onLayout
```

## 2. 多选题

1. 在使用super和this关键字时，以下描述错误的是

```
A. super()和this()不一定要放在构造方法内第一行
B. this()和super()可以同时出现在一个构造函数中
C. this()和super()可以在static环境中使用，
包括static方法和static语句块
D. 在子类构造方法中使用super()显示调用父类的构造方法，
super()必须写在子类构造方法的第一行，否则编译不通过
```

2. 关于广播说法正确的是

```
A. 动态注册的广播不解除注册也没关系
B. 有序广播是可以被拦截的
C. 当静态注册的广播设置的优先级高于动态注册的广播时，
静态注册将先接收到广播
D. 可以通过指定包名来发送定向广播
```

3. 关于IntentService和Service以下说法正确的是

```
A. IntentService任务执行完后会自动停止，service不会自动停止
B. Intentservice和service都需要创建新的线程来执行耗时任务
C. 每次启动IntentService,它的onStartCommand方法就会调用一次
D. 提交多个任务给IntentService,这些任务是并行执行的
```

4. Intent可以传递的数据类型包括

```
A. Bundle
B. Serializable
C. CharSequence
D. Parcelable
```

5. 下列哪几种情况可能会导致系统ANR

```
A. Activity的onCreate方法中进行耗时操作
B. IntentService的onHandleIntent方法中进行耗时操作
C. Broadcaster的onReceive方法中进行耗时操作
D. ContentProvider的onCreate方法中进行耗时操作
```

6. 下列哪几种情况可能会导致内存泄露

```
A. 单实例类中包含Acitvity Context成员变量
B. Activity使用AsyncTask执行耗时较长的任务时，频繁进行横竖屏切换操作
C. Activity中包含匿名Thread内部类，该Thread一直在后台运行
D. Activity的onCreate中进行大量内存申请操作
```

7. 下列关于synchronized的描述，那几项是正确的

```
A. 一个线程访问对象的synchronized(this)同步代码块时，
其它线程可以访问该对象中的其它synchronized(this)同步代码块
B. 一个线程访问对象的synchronized(this)同步代码块时，
其它线程可以访问该对象中的synchronized(otherLock)同步代码块
C. 两个并发线程访问同一个对象中的synchronized(this)
同步代码块时，同一时间内只能有一个线程拥有执行权
D. Object的wait()和notify()函数，只能在synchronized代码块中使用
```

8. 下列关于 Java 中多线程的描述，哪几项是正确的

```
A. 一个线程可以调用 yield 方法使其他线程有机会运行
B. 一个线程在调用它的 start 方法之前，将一直处于出生期
C. 高优先级的可运行线程会抢占低优先级线程
D. 一个线程访问对象的synchronized(this)同步代码块时，
其它线程可以访问该对象中的其它synchronized(this)同步代码块
```

9. 以下集合对象中哪几个是线程安全的

```
A. ArrayList
B. Vector
C. Hashtable
D. Stack
```

10. 关于java内存的描述不正确的是

```
A. java中有GC机制，所以不会出现内存溢出的情况
B. GC扫描过程中有弱引用的对象，不管当前内存空间足够与否，都会回收它的内存
C. 当GC执行时，会挂起其他线程的工作
D. 当开发人员把一个成员变量置空后，该对象占用的内存空间就会立马释放
```

## 3. 填空题

1. 从A切换到B activity时，会依次调用B生命周期的_____________________________________函数。
2. 一个有i层的二叉树，他的最小、最大节点数分别是_________、______________。
3. 一个Handler允许发送和处理____________或者_____________对象，并且会关联到主线程的MessageQueue中。
4. 若一序列进栈顺序为a1,a2,a3,a4，存在_____种可能的出栈序列。
5. Activity的launchMode有___________________________________________________________。

## 4. 算法题

1. 反转一个单链表。

```java
/**
 * Definition for singly-linked list.
 * public class ListNode {
 *     int val;
 *     ListNode next;
 *     ListNode(int x) { val = x; }
 * }
 */
class Solution {
    public ListNode reverseList(ListNode head) {
       
    }
}
```

2. 输入一颗二叉树的跟节点和一个整数，打印出二叉树中结点值的和为输入整数的所有路径。路径定义为从树的根结点开始往下一直到叶结点所经过的结点形成一条路径。(注意: 在返回值的list中，数组长度大的数组靠前)

```java
import java.util.ArrayList;
/**
public class TreeNode {
    int val = 0;
    TreeNode left = null;
    TreeNode right = null;

    public TreeNode(int val) {
        this.val = val;
    }
}
*/
public class Solution {
    public ArrayList<ArrayList<Integer>> FindPath(TreeNode root,int target) {

    }
}
```

3. 输入一个整数数组，实现一个函数来调整该数组中数字的顺序，使得所有的奇数位于数组的前半部分，所有的偶数位于数组的后半部分，并保证奇数和奇数，偶数和偶数之间的相对位置不变。

```java
public class Solution {
    public void reOrderArray(int [] array) {
   
    }
}
```

4. 给一个数组，返回它的最大连续子序列的和，例如:{6,-3,-2,7,-15,1,2,2},连续子向量的最大和为8(从第0个开始,到第3个为止)。

```java
public class Solution {
    public int FindGreatestSumOfSubArray(int[] array) {

    }
}
```

5. 快速排序代码实现

```java
public class QuickSort {
    public static void quickSort(int a[]) {

    }
}
```

---

## 答案

单选 1-10

CBCCABCBDC

多选 1-10

1. ABC 
2. BD
3. AC
4. ABCD
5. ACD
6. ABC
7. BCD
8. ABC
9. BCD
10. AD

填空
1. onCreate，onStart， onResume
2. i，$2^i - 1$
3. Message,Runnable
4. 14
5. standard，singleTop，singleTask，singleInstance


算法

1. 考察链表的操作
   
```java
class Solution {
    public ListNode reverseList(ListNode head) {
        ListNode prev = null; //前指针节点
        ListNode curr = head; //当前指针节点
        //每次循环，都将当前节点指向它前面的节点，然后当前节点和前节点后移
        while (curr != null) {
            ListNode nextTemp = curr.next; 
            //临时节点，暂存当前节点的下一节点，用于后移
            curr.next = prev; //将当前节点指向它前面的节点
            prev = curr; //前指针后移
            curr = nextTemp; //当前指针后移
        }
        return prev;
    }
}
```

2. 考察二叉树，递归

```java
public class Solution {
    private ArrayList<ArrayList<Integer>> listAll = 
                        new ArrayList<ArrayList<Integer>>();
    private ArrayList<Integer> list = new ArrayList<Integer>();
    public ArrayList<ArrayList<Integer>> FindPath(TreeNode root,int target) {
        if(root == null) return listAll;
        list.add(root.val);
        target -= root.val;
        if(target == 0 && root.left == null && root.right == null)
            listAll.add(new ArrayList<Integer>(list));
        FindPath(root.left, target);
        FindPath(root.right, target);
        list.remove(list.size()-1);
        return listAll;
    }
}
```

3. 考察数组

```java
public class Solution {
    public void reOrderArray(int [] array) {
       for(int i= 0;i<array.length-1;i++){
            for(int j=0;j<array.length-1-i;j++){
                if(array[j]%2==0&&array[j+1]%2==1){
                    int t = array[j];
                    array[j]=array[j+1];
                    array[j+1]=t;
                }
            }
        }
    }
}
```

4. 考察动态规划

```java
public int FindGreatestSumOfSubArray(int[] array) {
        int res = array[0]; //记录当前所有子数组的和的最大值
        int max = array[0];   //包含array[i]的连续数组最大值
        for (int i = 1; i < array.length; i++) {
            max=Math.max(max+array[i], array[i]);
            res=Math.max(max, res);
        }
        return res;
}
```

5. 考察排序算法

```java
public class QuickSort {
    public static void sort(int a[], int low, int hight) {
        int i, j, index;
        if (low > hight) {
            return;
        }
        i = low;
        j = hight;
        index = a[i]; // 用子表的第一个记录做基准
        while (i < j) { // 从表的两端交替向中间扫描
            while (i < j && a[j] >= index)
                j--;
            if (i < j)
                a[i++] = a[j];// 用比基准小的记录替换低位记录
            while (i < j && a[i] < index)
                i++;
            if (i < j) // 用比基准大的记录替换高位记录
                a[j--] = a[i];
        }
        a[i] = index;// 将基准数值替换回 a[i]
        sort(a, low, i - 1); // 对低子表进行递归排序
        sort(a, i + 1, hight); // 对高子表进行递归排序
    }
    public static void quickSort(int a[]) {
        sort(a, 0, a.length - 1);
    }
}
```

