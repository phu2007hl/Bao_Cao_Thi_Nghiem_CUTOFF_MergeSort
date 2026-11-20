# Thí nghiệm CUTOFF cho MergeSort

## Thông tin

- **Sinh viên:** Đặng Đức Phú
- **MSSV:** 25020316
- **Lớp:** K70I-IT1
- **Môn học:** Cấu trúc dữ liệu và giải thuật

## 1. Mục tiêu

MergeSort và Quicksort có thể được cải tiến bằng cách sử dụng InsertionSort khi đoạn con đủ nhỏ. Giáo trình thường đề cập đến `CUTOFF = 7` và `CUTOFF = 10`, nhưng giá trị phù hợp còn phụ thuộc vào máy, kích thước và dạng dữ liệu.

Project thực hiện các mục tiêu sau:

1. Cài đặt MergeSort kết hợp InsertionSort theo nội dung bài giảng.
2. Khảo sát 18 giá trị CUTOFF từ 1 đến 100.
3. Đo thời gian trên 13 bộ dữ liệu có kích thước và phân phối khác nhau.
4. So sánh trực tiếp `CUTOFF = 7`, `10` và `12`.
5. Kiểm tra độ ổn định của kết quả qua 5 batch độc lập.
6. Tổng hợp, phân tích và trực quan hóa kết quả bằng bảng CSV và biểu đồ.

## 2. Ý tưởng thuật toán

MergeSort chia mảng thành hai nửa, sắp xếp đệ quy rồi trộn hai nửa đã có thứ tự. Khi đoạn con có kích thước nhỏ hơn ngưỡng CUTOFF, chương trình dừng đệ quy và gọi InsertionSort:

```java
if (hi <= lo + cutoff - 1) {
    Insertion.sort(a, lo, hi);
    return;
}
```

`CUTOFF = 1` được dùng làm mốc MergeSort thuần. CUTOFF quá nhỏ làm tăng chi phí đệ quy và trộn; CUTOFF quá lớn làm InsertionSort xử lý các đoạn dài hơn. Mục tiêu của thí nghiệm là quan sát sự đánh đổi này trên máy thực tế.

## 3. Cấu trúc project

```text
Bao_Cao_Thi_Nghiem_CUTOFF_MergeSort/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── README.md
│   └── generated/
├── logs/
│   └── README.md
├── report/
│   ├── report.md
│   ├── report_detailed.pdf
│   └── figures/
├── results/
│   ├── raw/
│   ├── summary/
│   ├── charts/
│   └── repeated/
│       ├── batch_1/ ... batch_5/
│       ├── summary/
│       └── charts/
├── scripts/
│   ├── generate_data.py
│   ├── run_experiments.py
│   ├── summarize_results.py
│   ├── plot_results.py
│   ├── run_repeated_experiments.py
│   ├── summarize_repeated.py
│   └── plot_repeated.py
└── src/
    ├── Main.java
    ├── algorithms/
    │   ├── Insertion.java
    │   └── Merge.java
    └── benchmark/
        ├── BenchmarkRunner.java
        ├── InputGenerator.java
        └── ResultValidator.java
```

Thư mục `build/` chỉ là thư mục biên dịch tạm thời và được loại khỏi repository bằng `.gitignore`.

## 4. Bộ dữ liệu

Project sử dụng 13 bộ dữ liệu:

- `random_10000` đến `random_1000000`: dữ liệu giả ngẫu nhiên với nhiều kích thước.
- `sorted_100000`: mảng đã tăng dần.
- `reversed_100000`: mảng giảm dần.
- `nearly_sorted_100000`: mảng gần có thứ tự, khoảng 1% vị trí bị hoán đổi.
- `few_distinct_100000`: mảng chỉ có 10 giá trị phân biệt.
- `all_equal_100000`: mọi phần tử bằng nhau.
- `edge_values_10000`: dữ liệu có các giá trị biên của kiểu `int`.

Dữ liệu được sinh với seed `20261116`. Chi tiết định dạng và cách tái tạo nằm trong [data/README.md](data/README.md).

## 5. Môi trường thực nghiệm

- **CPU:** 12th Gen Intel(R) Core(TM) i7-1265U, 2.70 GHz
- **RAM:** 16 GB, 5200 MT/s
- **GPU:** Intel(R) Iris(R) Xe Graphics
- **Hệ điều hành:** Windows 10 Pro, version 26H2, build 26300.9974
- **JDK:** Java 25.0.2 LTS
- **JVM:** HotSpot 64-Bit Server VM
- **Bộ định thời:** `System.nanoTime()`

## 6. Cài đặt

### 6.1. Java

Cài đặt JDK và bảo đảm `java` và `javac` có trong `PATH`. Nếu máy có nhiều JDK, đặt biến môi trường `JAVA_HOME` trỏ đến JDK muốn sử dụng.

### 6.2. Python

Cài đặt các thư viện cần cho sinh kết quả tổng hợp và vẽ biểu đồ:

```powershell
python -m pip install -r requirements.txt
```

Các thư viện gồm NumPy, Matplotlib, pandas và SciPy.

## 7. Chạy project

Các lệnh sau được thực hiện từ thư mục gốc project.

### 7.1. Biên dịch mã Java

```powershell
New-Item -ItemType Directory -Force build
javac -d build (Get-ChildItem -Recurse src -Filter *.java | ForEach-Object FullName)
```

### 7.2. Sinh dữ liệu

```powershell
java -cp build Main generate data/generated 20261116
```

### 7.3. Chạy benchmark lần đơn

```powershell
python scripts/run_experiments.py
```

Benchmark lần đơn sử dụng 3 vòng warm-up và 10 lần đo cho mỗi CUTOFF. Thứ tự CUTOFF được xáo trộn có kiểm soát. Thời gian sao chép mảng và kiểm tra kết quả không nằm trong vùng đo.

### 7.4. Tổng hợp và vẽ biểu đồ lần đơn

```powershell
python scripts/summarize_results.py
python scripts/plot_results.py
```

### 7.5. Chạy thí nghiệm lặp lại

```powershell
python scripts/run_repeated_experiments.py
python scripts/summarize_repeated.py
python scripts/plot_repeated.py
```

Thí nghiệm lặp lại gồm 5 batch. Mỗi batch có 20 lần đo cho từng CUTOFF và 3 vòng warm-up. Seed xáo trộn của mỗi batch được thay đổi theo quy tắc:

```text
20261116 + batch * 1009
```

## 8. Kiểm tra tính đúng

Sau mỗi lần đo, kết quả được kiểm tra bằng `ResultValidator`:

1. Độ dài mảng không thay đổi.
2. Mảng kết quả có thứ tự không giảm.
3. Từng phần tử khớp với bản sao chuẩn đã được sắp xếp.

Nếu kết quả sai, benchmark dừng và phát sinh lỗi. Nhờ đó các thời gian được lưu đều tương ứng với một lần sắp xếp hợp lệ.

## 9. Kết quả đầu ra

### `results/raw/`

- `<dataset>.csv`: median và min theo từng CUTOFF.
- `runs_<dataset>.csv`: thời gian của từng lần đo, gồm các cột `run_index`, `cutoff`, `elapsed_ns` và `elapsed_ms`.

### `results/summary/`

- `summary.csv`: CUTOFF tốt nhất trong lần chạy đơn.
- `table_cutoff_ranges_by_N.csv`: tổng hợp theo khoảng CUTOFF và kích thước N.
- `table_cutoff_by_distributions.csv`: so sánh các dạng dữ liệu.
- `analysis_stats_all.csv`: mean, median, min, SD và CV.
- `analysis_aggregate.csv`: thời gian chuẩn hóa trên nhóm random.
- `analysis_bootstrap_pairs.csv`: khoảng bootstrap cho các cặp CUTOFF.
- `analysis_mann_whitney.csv`: p-value Mann–Whitney theo kích thước.
- `analysis_distributions.csv`: phân tích theo phân phối dữ liệu.

### `results/repeated/summary/`

- `stable_best_cutoffs.csv`: CUTOFF có `mean_median_ms` thấp nhất qua 5 batch trên từng dataset.
- `cutoff_stability.csv`: mean, SD và số batch thắng của từng CUTOFF.
- `compare_7_10_12.csv`: so sánh CUTOFF = 7, 10, 12.
- `random_aggregate_repeated.csv`: kết quả chuẩn hóa tổng hợp trên nhóm random.

## 10. Tiêu chí phân tích

Tiêu chí chính của báo cáo là CUTOFF có `mean_median_ms` nhỏ nhất qua 5 batch trên từng dataset. Đây là tiêu chí được dùng để kết luận CUTOFF ổn định.

Các chỉ số `best_batch_count`, SD và CV dùng để đánh giá độ dao động. Bootstrap và Mann–Whitney là phân tích bổ trợ từ lần chạy đơn; do các lần đo dùng chung dữ liệu, JVM và điều kiện máy, các kết quả này được diễn giải thận trọng và không xem p-value là bằng chứng tuyệt đối.

## 11. Kết luận chính

- Không có một CUTOFF duy nhất tốt nhất cho mọi kích thước và phân phối dữ liệu.
- Dữ liệu sorted, nearly sorted và all equal thường phù hợp với CUTOFF lớn.
- Dữ liệu random thường có vùng tốt ở CUTOFF nhỏ hoặc trung bình.
- `CUTOFF = 7` và `CUTOFF = 10` đều là các lựa chọn hợp lý để bắt đầu.
- Nếu cần một mặc định dễ giải thích và bám sát giáo trình, có thể dùng `CUTOFF = 10`.
- Nếu tối ưu riêng cho nhóm random theo tiêu chí chuẩn hóa, `CUTOFF = 25` là ứng viên tốt nhất trong dữ liệu hiện tại.
- Khi biết trước loại dữ liệu và kích thước mảng, nên benchmark lại trên dữ liệu thực tế.

## 12. Tài liệu

- Báo cáo đầy đủ: [report/report_detailed.pdf](report/report_detailed.pdf)
- Báo cáo Markdown: [report/report.md](report/report.md)
- Biểu đồ: [report/figures](report/figures)
- Nhật ký chat AI: [logs/README.md](logs/README.md)
- Mô tả dữ liệu: [data/README.md](data/README.md)

Tài liệu tham khảo lý thuyết gồm giáo trình/bài giảng môn học, *Algorithms, 4th Edition* của Robert Sedgewick và Kevin Wayne, cùng Java API về `System.nanoTime`, `Arrays` và `Comparable`.
