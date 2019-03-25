import java.util.concurrent.ConcurrentHashMap;

class Main{
    public static void main(String[] args) {
        // AtomicInteger i = new AtomicInteger(0);
        // i.getAndIncrement();
        // System.out.print(i);
        // int a = 1;
        // int b = 1;
        Integer a = new Integer(1);
        Integer b = new Integer(1);
        System.out.print(a == b);
        ConcurrentHashMap map = new ConcurrentHashMap();
    }
}