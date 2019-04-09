
public class Main {
    public static void main(String[] args) {
        split(12);
    }

    public static int split(int number) {
        if (number > 1) {
            if (number % 2 != 0) {
                int n1 = split((number + 1) / 2);
                System.out.print(n1);
            }
            int n2 = split(number / 2);
            System.out.print(n2);
        }
        return number;
    }
}
