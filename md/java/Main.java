import java.util.concurrent.atomic.*;

class Main{
    public static void main(String[] args) {
        AtomicInteger i = new AtomicInteger(0);
        i.getAndIncrement();
        System.out.print(i);
    }
}