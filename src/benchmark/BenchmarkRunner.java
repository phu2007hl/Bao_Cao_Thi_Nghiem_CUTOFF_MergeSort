package benchmark;

import algorithms.Merge;
import java.io.*;
import java.nio.file.*;
import java.util.*;

public final class BenchmarkRunner {
    public static final int[] CUTOFFS = {1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40, 50, 75, 100};

    private BenchmarkRunner() {}

    public static void run(Path input, Path output, int repeat, int warmup) throws IOException {
        run(input, output, repeat, warmup, 20261116L);
    }

    public static void run(Path input, Path output, int repeat, int warmup, long shuffleSeed) throws IOException {
        if (repeat < 1 || warmup < 0) throw new IllegalArgumentException("repeat and warmup are invalid");
        Integer[] data = load(input);
        long[][] times = measure(data, repeat, warmup, shuffleSeed);
        Path parent = output.getParent();
        if (parent != null) Files.createDirectories(parent);

        try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(output))) {
            out.println("cutoff,median_ms,min_ms");
            for (int i = 0; i < CUTOFFS.length; i++) {
                double median = median(times[i]) / 1e6;
                double min = Arrays.stream(times[i]).min().orElse(0) / 1e6;
                out.printf(Locale.US, "%d,%.3f,%.3f%n", CUTOFFS[i], median, min);
            }
        }

        Path runs = output.resolveSibling("runs_" + output.getFileName());
        try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(runs))) {
            out.println("run_index,cutoff,elapsed_ns,elapsed_ms");
            for (int r = 0; r < repeat; r++)
                for (int i = 0; i < CUTOFFS.length; i++)
                    out.printf(Locale.US, "%d,%d,%d,%.6f%n", r + 1, CUTOFFS[i], times[i][r], times[i][r] / 1e6);
        }
    }

    private static long[][] measure(Integer[] data, int repeat, int warmup, long shuffleSeed) {
        long[][] times = new long[CUTOFFS.length][repeat];
        Integer[] expected = data.clone();
        Arrays.sort(expected);
        Random random = new Random(shuffleSeed ^ data.length);
        ArrayList<Integer> order = new ArrayList<>();
        for (int i = 0; i < CUTOFFS.length; i++) order.add(i);
        for (int w = 0; w < warmup; w++) {
            Collections.shuffle(order, random);
            for (int index : order) Merge.sort(data.clone(), CUTOFFS[index]);
        }

        for (int r = 0; r < repeat; r++) {
            Collections.shuffle(order, random);
            for (int index : order) {
                int cutoff = CUTOFFS[index];
                Integer[] a = data.clone();
                long start = System.nanoTime();
                Merge.sort(a, cutoff);
                times[index][r] = System.nanoTime() - start;
                if (!ResultValidator.matchesExpected(a, expected))
                    throw new IllegalStateException("Sort sai ở cutoff " + cutoff);
            }
        }
        return times;
    }

    private static double median(long[] values) {
        long[] sorted = values.clone();
        Arrays.sort(sorted);
        int n = sorted.length;
        return n % 2 == 1 ? sorted[n / 2] : (sorted[n / 2 - 1] + sorted[n / 2]) / 2.0;
    }

    private static Integer[] load(Path path) throws IOException {
        ArrayList<Integer> values = new ArrayList<>();
        try (BufferedReader br = Files.newBufferedReader(path)) {
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (!line.isEmpty()) values.add(Integer.parseInt(line));
            }
        }
        return values.toArray(new Integer[0]);
    }
}

