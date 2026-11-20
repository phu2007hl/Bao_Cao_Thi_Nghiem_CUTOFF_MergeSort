import benchmark.*;
import java.nio.file.*;

public final class Main {
    public static void main(String[] args) throws Exception {
        if (args.length == 0 || args[0].equals("help")) {
            System.out.println("Usage:");
            System.out.println("  Main generate <output-dir> [seed]");
            System.out.println("  Main benchmark <input-file> <output-csv> [repeat] [warmup] [shuffle-seed]");
            return;
        }
        switch (args[0]) {
            case "generate" -> InputGenerator.generateAll(Path.of(args[1]), args.length > 2 ? Long.parseLong(args[2]) : 20261116L);
            case "benchmark" -> BenchmarkRunner.run(Path.of(args[1]), Path.of(args[2]), args.length > 3 ? Integer.parseInt(args[3]) : 20, args.length > 4 ? Integer.parseInt(args[4]) : 5, args.length > 5 ? Long.parseLong(args[5]) : 20261116L);
            default -> throw new IllegalArgumentException("Unknown command: " + args[0]);
        }
    }
}

