public class code{
    public static void main(String[] args) {
        System.out.print(Demo.i);
        Singleton a = Singleton.getInstance();
        Singleton b = Singleton.getInstance();
        System.out.print(a == b);
    }
}

class Demo{
    static {
        i = 100;
    }
    public static int i = 10;
}

class Singleton{
    private Singleton(){}

    private static class SingletonHolder{
        private static final Singleton Instance = new Singleton();
    }

    public static Singleton getInstance(){
        return SingletonHolder.Instance;
    }
}