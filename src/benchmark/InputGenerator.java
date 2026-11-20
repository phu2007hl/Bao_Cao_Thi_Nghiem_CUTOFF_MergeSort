package benchmark;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public final class InputGenerator {
    private InputGenerator() {}

    public static void generateAll(Path output, long seed) throws IOException {
        Files.createDirectories(output);
        Random random = new Random(seed);
        int[] sizes = {10_000, 20_000, 50_000, 100_000, 200_000, 500_000, 1_000_000};
        for (int n : sizes) write(output.resolve("random_" + n + ".txt"), randomArray(n, random));
        int n = 100_000;
        int[] base = randomArray(n, random);
        Arrays.sort(base);
        write(output.resolve("sorted_" + n + ".txt"), base.clone());
        reverse(base);
        write(output.resolve("reversed_" + n + ".txt"), base.clone());
        reverse(base);
        for (int k = 0; k < n / 100; k++) swap(base, random.nextInt(n), random.nextInt(n));
        write(output.resolve("nearly_sorted_" + n + ".txt"), base);
        int[] few = new int[n];
        for (int i = 0; i < n; i++) few[i] = random.nextInt(10);
        write(output.resolve("few_distinct_" + n + ".txt"), few);
        write(output.resolve("all_equal_" + n + ".txt"), new int[n]);
        int[] edge = new int[10_000];
        for (int i = 0; i < edge.length; i++) edge[i] = random.nextInt();
        edge[0] = Integer.MIN_VALUE;
        edge[1] = -1;
        edge[2] = 0;
        edge[3] = Integer.MAX_VALUE;
        write(output.resolve("edge_values_10000.txt"), edge);
    }

    private static int[] randomArray(int n, Random random) {
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = random.nextInt(1_000_000_001);
        return a;
    }

    private static void write(Path file, int[] a) throws IOException {
        try (BufferedWriter out = Files.newBufferedWriter(file)) {
            for (int x : a) { out.write(Integer.toString(x)); out.newLine(); }
        }
    }

    private static void swap(int[] a, int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }
    private static void reverse(int[] a) { for (int i = 0, j = a.length - 1; i < j; i++, j--) swap(a, i, j); }
}

