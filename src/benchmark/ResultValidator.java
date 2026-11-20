package benchmark;

public final class ResultValidator {
    private ResultValidator() {}

    public static boolean isSorted(Comparable[] a) {
        for (int i = 1; i < a.length; i++)
            if (a[i].compareTo(a[i - 1]) < 0) return false;
        return true;
    }

    public static boolean matchesExpected(Comparable[] actual, Comparable[] expected) {
        if (actual.length != expected.length || !isSorted(actual)) return false;
        for (int i = 0; i < actual.length; i++)
            if (actual[i].compareTo(expected[i]) != 0) return false;
        return true;
    }
}

