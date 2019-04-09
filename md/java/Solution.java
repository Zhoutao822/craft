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